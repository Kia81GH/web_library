from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from library.models import Book,Member,Loan
from datetime import datetime

# Create your views here.
def index_view(request):
    now = datetime.now()
    ms="سلام به دانشجویان بیرکار"
    context={"date":now,"text":ms}
    return render(request,'home.html', context)

def book_list_view(request):
    books = Book.objects.all()

    context = {
        "books": books,
    }

    return render(request, "book_list.html", context)

def member_list_view(request):
    members = Member.objects.all()
    context = {"members":members}
    return render(request,'member_list.html', context)

def loan_list_view(request):
    loans = (
        Loan.objects
        .select_related("book", "member")
        .order_by("-loan_date", "-id")
    )

    context = {
        "loans": loans,
        "today": timezone.localdate(),
    }

    return render(request, "loan_list.html", context)

@require_POST
def loan_return_view(request, pk):
    # فقط امانتی که هنوز بازگشت آن ثبت نشده است
    loan = get_object_or_404(
        Loan,
        pk=pk,
        return_date__isnull=True,
    )

    # تاریخ تحویل واقعی؛ مستقل از موعد بازگشت
    loan.return_date = timezone.localdate()
    loan.save()

    return redirect("loan_list")