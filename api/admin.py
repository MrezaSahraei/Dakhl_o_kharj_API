from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Category)
class CategoryModelNameAdmin(admin.ModelAdmin):
    fields = ['user', 'name', 'category_type', 'color', 'default_amount', 'is_active']
    ordering = ['created_at']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    fields = ['user', 'category', 'amount', 'description', 'date', 'record_date']
    ordering = ['created_at']

@admin.register(Budgeting)
class BudgetingAdmin(admin.ModelAdmin):
    fields = ['user', 'category', 'minimum_target_amount','maximum_target_amount', 'start_date', 'end_date']
    ordering = ['created_at']


