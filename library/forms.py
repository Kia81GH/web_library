from django import forms
from django.utils import timezone
from .models import Book, Member, Loan

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            "first_name",
            "last_name",
            "membership_code",
            "birth_year",
        ]

        error_messages = {
            "membership_code": {
                "unique": "این کد عضویت قبلاً ثبت شده است.",
            },
        }

    def clean_birth_year(self):
        birth_year = self.cleaned_data["birth_year"]

        if birth_year <= 0:
            raise forms.ValidationError(
                "سال تولد باید عددی مثبت باشد."
            )

        return birth_year

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = [
            "book",
            "member",
            "due_date",
        ]

        widgets = {
            "due_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date"},
            ),
        }

        help_texts = {
            "due_date": "موعد بازگشت را به تاریخ میلادی انتخاب کنید.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # کتاب‌هایی که هنوز امانت باز دارند
        open_book_ids = Loan.objects.filter(
            return_date__isnull=True
        ).values_list("book_id", flat=True)

        # فقط کتاب‌های قابل امانت در فرم نمایش داده شوند
        self.fields["book"].queryset = (
            Book.objects
            .filter(is_available=True)
            .exclude(pk__in=open_book_ids)
            .order_by("title")
        )

        self.fields["member"].queryset = (
            Member.objects
            .order_by("last_name", "first_name")
        )

        self.fields["book"].empty_label = "کتاب را انتخاب کنید"
        self.fields["member"].empty_label = "عضو را انتخاب کنید"

        # در فرم ثبت امانت، واردکردن موعد الزامی است
        self.fields["due_date"].required = True
        self.fields["due_date"].input_formats = ["%Y-%m-%d"]

    def clean_due_date(self):
        due_date = self.cleaned_data["due_date"]

        if due_date < timezone.localdate():
            raise forms.ValidationError(
                "موعد بازگشت نمی‌تواند قبل از امروز باشد."
            )

        return due_date
