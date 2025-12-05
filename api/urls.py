from django.contrib import admin
from django.urls import path, include
from . import views
app_name = 'api'

urlpatterns = [
    path('categories/', views.CategoryListCreateAPIView.as_view(),name='category-list-create'),

    path('categories/<int:pk>/', views.CategoryRetrieveUpdateDestroyAPIView.as_view(),name='category-detail'),

    path('transactions/', views.TransactionListCreateAPIView.as_view(),name='transaction-list-create'),

    path('transactions/<int:pk>/', views.TransactionRetrieveUpdateDestroyAPIView.as_view(),name='transaction-detail'),

    path('budgeting/', views.BudgetingListCreateAPIView.as_view(), name='budget-list-create'),

    path('budgeting/<int:pk>', views.BudgetingRetrieveUpdateDestroyAPIView.as_view(), name='budget_detail'),

    path('user-balance/', views.UserBalanceAPIView.as_view(), name='user_balance'),

    path('user-balance/monthly', views.MonthlySummaryAPIView.as_view(), name='monthly_balance'),

    path('user-balance/yearly', views.YearlySummaryAPIView.as_view(), name='yearly_balance')
]