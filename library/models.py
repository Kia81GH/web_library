from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone

class Book(models.Model):
    book_code = models.CharField(max_length=20,unique=True,verbose_name="کد کتاب")
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان کتاب"
    )

    author = models.CharField(
        max_length=150,
        verbose_name="نویسنده"
    )

    publication_year = models.IntegerField(
        verbose_name="سال نشر"
    )

    page_count = models.IntegerField(
        verbose_name="تعداد صفحات"
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name="در دسترس"
    )

    def __str__(self):
        return f"{self.title} - {self.author}"          
    
    def update_availability(self):
        """
        وضعیت «در دسترس» کتاب را از روی امانتهای بازِ همین کتاب دوباره حساب میکند.
        کتاب وقتی در دسترس است که هیچ امانتِ باز (بدون تاریخ بازگشت) نداشته باشد.
        """
        # آیا امانتی برای این کتاب هست که هنوز برنگشته است؟
        has_open_loan = Loan.objects.filter(book=self, return_date__isnull=True).exists()

        # اگر امانتِ باز دارد => در دسترس نیست ؛ در غیر این صورت => در دسترس است
        self.is_available = not has_open_loan

        # فقط همان یک فیلد را ذخیره میکنیم (بقیه فیلدها دستنخورده میمانند)
        self.save(update_fields=["is_available"])


class Member(models.Model):
    first_name = models.CharField(
        max_length=100,
        verbose_name="نام"
    )

    last_name = models.CharField(
        max_length=100,
        verbose_name="نام خانوادگی"
    )

    membership_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="کد عضویت"
    )

    birth_year = models.IntegerField(
        verbose_name="سال تولد"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Loan(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        verbose_name="کتاب"
    )

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        verbose_name="عضو"
    )

    loan_date = models.DateField(
        auto_now_add=True,
        verbose_name="تاریخ امانت"
    )

    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="موعد بازگشت"
    )

    return_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ بازگشت واقعی"
    )

    def __str__(self):
        return f"{self.book} - {self.member}"

    def save(self, *args, **kwargs):
        # اگر این امانت قبلاً وجود داشته و کتابش عوض شده باشد،
        # باید کتابِ قبلی را هم بعداً بهروزرسانی کنیم.
        previous_book = None

        if self.pk:  # pk دارد => ویرایش میشود، نه ساخت جدید
            previous_book_id = (
                Loan.objects.filter(pk=self.pk)
                .values_list("book_id", flat=True)
                .first()
            )
            if previous_book_id and previous_book_id != self.book_id:
                previous_book = Book.objects.filter(pk=previous_book_id).first()

        # ۱) اول خودِ امانت ذخیره شود
        super().save(*args, **kwargs)

        # ۲) وضعیت کتابِ فعلی از روی دیتابیس دوباره حساب شود
        self.book.update_availability()

        # ۳) اگر کتاب عوض شده بود، کتابِ قبلی هم بهروز شود
        if previous_book is not None:
            previous_book.update_availability()

# ---------------------------------------------------------------------------
# سیگنال post_delete : هر بار که یک Loan حذف شود (از هر راهی) اجرا میشود
# ---------------------------------------------------------------------------
@receiver(post_delete, sender=Loan)
def loan_deleted(sender, instance, **kwargs):
    """
    وقتی امانت پاک میشود، وضعیت کتابش باید دوباره حساب شود.
    این سیگنال همهٔ راههای حذف را پوشش میدهد:
        - loan.delete()
        - Loan.objects.filter(...).delete()
        - اکشن «حذف امانتهای انتخابشده» در ادمین
        - حذف کتاب (cascade)
    """
    book_pk = instance.book_id
    # اگر خودِ کتاب هم پاک شده باشد، کاری برای انجام دادن نیست
    book = Book.objects.filter(pk=book_pk).first()
    if book is not None:
        book.update_availability()
