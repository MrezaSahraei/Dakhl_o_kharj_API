from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import AppUser
from django.conf import settings
# Create your models here.

class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

class Category(TimeStamp):
    TYPE_CHOICES = (
        ('income', 'درآمد'),
        ('expense', 'هزینه ضروری'),
        ('savings', 'پس‌انداز/سرمایه‌گذاری'),
    )
    COLORS = (
        ('سبز', '#00A878'),
        ('آبی','#2C73D2' ),
        ('قرمز', '#E94F64'),
        ('نارنجی', '#FF7B29'),
        ('بنفش', '#8E7DBE'),
        ('خاکستری', '#AAB8C2')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='expense')
    color = models.CharField(max_length=100, choices=COLORS, default='Gray')
    default_amount = models.PositiveIntegerField(default=0, null=True, blank=True, help_text='واحد پیش ‌فرض (ریال)')
    is_active = models.BooleanField(default=True)

    class Meta(TimeStamp.Meta):
        ordering = ['name']
        unique_together = ('name', 'user')

    def __str__(self):
        return f'{self.user} {self.category_type}: {self.name}'

class Transaction(TimeStamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')
    amount = models.PositiveIntegerField(default=0, help_text='واحد پیش‌فرض (ریال)')
    description = models.TextField(blank=True, null=True)
    transaction_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.category.name}: {self.amount}'

class Budgeting(TimeStamp):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_budget')
    minimum_target_amount = models.PositiveIntegerField(default=0, help_text='واحد پیش‌فرض (ریال)')
    maximum_target_amount = models.PositiveIntegerField(default=0, help_text='واحد پیش‌فرض (ریال)')
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta(TimeStamp.Meta):
        ordering = ['-start_date']
        unique_together = ('user', 'category', 'start_date', 'end_date')