from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),#library::index book_list
    path("books/", views.book_list_view, name="book_list"),
    path('memberlist/', views.member_list_view, name='member_list'),
    path('loanlist/', views.loan_list_view, name='loan_list'),
    path('loan/<int:pk>/return/', views.loan_return_view, name='loan_return')
]