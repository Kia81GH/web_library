from django.contrib import admin
from .models import Book, Member, Loan

class BookAdmin(admin.ModelAdmin):
    fields = ["book_code", "title", "author", "publication_year", "page_count"]
    list_display = ["book_code", "title", "author", "publication_year", "page_count", "is_available"]
    list_filter = ["is_available"]

class MemberAdmin(admin.ModelAdmin):
    fields = ["membership_code", "first_name", "last_name", "birth_year"]
    list_display = ["membership_code", "first_name", "last_name", "birth_year"]

class LoanAdmin(admin.ModelAdmin):
    fields = ["book", "member", "due_date", "return_date"]
    list_display = [
        "book",
        "member",
        "loan_date",
        "due_date",
        "return_date",
    ]
    list_filter = ["return_date"]

admin.site.register(Book, BookAdmin)
# admin.site.register(Book)
admin.site.register(Member, MemberAdmin)
admin.site.register(Loan, LoanAdmin)
