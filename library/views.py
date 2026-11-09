from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import MemberForm, LoanForm, BookForm
from .models import Book, Member, Loan

def index_view(request):
    now = datetime.now()

    context = {
        "date": now,
        "text": "سلام به دانشجویان بیرکار",
    }

    return render(request, "home.html", context)

def book_list_view(request):
    if request.method == "POST":
        form = BookForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("book_list")
    else:
        form = BookForm()

    books = Book.objects.all().order_by("-id")

    context = {
        "books": books,
        "form": form,
    }

    return render(request, "book_list.html", context)

def member_list_view(request):
    if request.method == "POST":
        # فرم همراه با اطلاعات ارسال‌شده توسط کاربر
        form = MemberForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("member_list")
    else:
        # فرم خالی برای اولین نمایش صفحه
        form = MemberForm()

    members = Member.objects.all().order_by("-id")

    context = {
        "members": members,
        "form": form,
    }

    return render(request, "member_list.html", context)

def loan_list_view(request):
    if request.method == "POST":
        form = LoanForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("loan_list")
    else:
        form = LoanForm()

    loans = (
        Loan.objects
        .select_related("book", "member")
        .order_by("-loan_date", "-id")
    )

    context = {
        "loans": loans,
        "form": form,
        "today": timezone.localdate(),
    }

    return render(request, "loan_list.html", context)

@require_POST
def loan_return_view(request, pk):
    loan = get_object_or_404(
        Loan,
        pk=pk,
        return_date__isnull=True,
    )

    loan.return_date = timezone.localdate()
    loan.save()

    return redirect("loan_list")
