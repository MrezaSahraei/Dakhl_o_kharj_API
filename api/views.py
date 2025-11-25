from django.core.serializers import serialize
from django.shortcuts import render
from pyexpat.errors import messages
from rest_framework.response import Response
from rest_framework.views import APIView, status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from .serializers import CategorySerializer
from .models import *
from django.db.models import Sum, DecimalField
from datetime import date
# Create your views here.

'''class CategoryListCreateAPIView(APIView):
    def get(self, request):
        categories = Category.objects.filter(user=request.user)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.Http_201_CREATED)'''

class CategoryListCreateAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def preform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({'detail': 'خطای دیتابیس هنگام اپدیت دسته'})

class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def preform_update(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({'detail': 'خطای دیتابیس هنگام اپدیت دسته'})

    def preform_destroy(self, instance):
        if instance.transactions.exists():
            raise ValidationError({'detail':'عدم امکان حذف زیرا تراکنش هایی به آن مرنبط است'})
        if instance.category_budget.exists():
            raise ValidationError({'detail':'عدم امکان حذف زیرا بودجه بندی هایی برای ان وجود دارند'})
        instance.delete()

class TransactionListCreateAPIView(generics.ListAPIView):
    queryset = Transaction
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.select_related('category').filter(user=self.request.user)

    def preform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({'detail': 'خطای دیتابیس هنگام ساخت رکورد تراکنش'})

class TransactionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.select_related('category').filter(user=self.request.user)

    def preform_update(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({'detail': 'خطای دیتابیس هنگام اپدیت تراکنش ها'})


class BudgetingListCreateAPIView(generics.ListCreateAPIView):
    queryset = Budgeting
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budgeting.objects.select_related('category').filter(user=self.request.user)

    def preform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({'detail': 'خطای دیتابیس هنگام اپدیت بودجه'})

class BudgetingRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Budgeting
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budgeting.objects.select_related('category').filter(user=self.request.user)

    def preform_update(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({'detail': 'خطای دیتابیس هنگام اپدیت بودجه'})

class UserBalanceAPIView(APIView):

    def calculate_balance(self, request):
        user = request.user
        total_income = (Transaction.objects.select_related('category', 'user').
                        filter(user=user, category__category_type='income')).aggregate(total=Sum('amount'))['total'] or 0

        total_expense = (Transaction.objects.select_related('category', 'user').
                        filter(user=user, category__category_type='expense')).aggregate(total=Sum('amount'))['total'] or 0

        final_balance = total_income - total_expense

        return total_income, total_expense, final_balance

    def get(self, request):
        user = request.user
        total_income, total_expense, final_balance = self.calculate_balance(user)

        if final_balance < 0:
            final_balance_display = abs(final_balance)
            balance_status = 'تراز شما منفی است.'
        else:
            final_balance_display = final_balance
            balance_status = 'تراز شما مثبت است.(میتوانید این مبلغ را در دسته پس انداز بگذارید.)'

        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'net_balance': final_balance_display,
            'balance_status': balance_status
        })

    #Automatic saving feature
    def post(self,request):
        user = request.user
        total_income, total_expense, final_balance = self.calculate_balance(user)

        confirm_saving = request.data.get('confirm_saving', False)
        if confirm_saving:

            if final_balance > 0:

                '''create_category = Category.objects.get_or_create(
                    user=user,
                    category_type='savings',
                    defaults={'name': 'پس‌انداز', 'color': 'سبز'})'''
                saving_category, created = Category.objects.get_or_create(category_type='savings',
                defaults={'name': 'savings'})

                Transaction.objects.create(
                    user=user, amount=final_balance, category=saving_category,
                    description="پس‌انداز خودکار مازاد تراز مالی (ایجاد شده با مجوز کاربر)",
                    transaction_date=date.today()
                )

                if created:
                    message = f"دسته پس انداز ایجاد و مبلغ {final_balance} به عنوان پس‌انداز ثبت شد."
                else:
                    message = f"مبلغ {final_balance} به عنوان پس‌انداز ثبت شد."

                return Response({
                    'status': 'success',
                    'saved_amount': final_balance,
                    'message': message
                }, status=status.HTTP_201_CREATED)

            elif final_balance == 0:
                return Response({
                    'status': 'info',
                    'message': 'تراز شما 0 است برای پس انداز باید تراز مثبت داشته باشید'
                }, status=status.HTTP_200_OK)

            else:
                return Response({
                    'status': 'info',
                    'message': 'تراز شما منفی است برای پس انداز باید تراز مثبت داشته باشید'

                }, status=status.HTTP_200_OK)

        else:
            return Response({
                "status": "error",
                "message": "برای ذخیره مازاد باید مجوز پس انداز مازاد تراز مالی را ارسال کنید."
            }, status=status.HTTP_400_BAD_REQUEST)
