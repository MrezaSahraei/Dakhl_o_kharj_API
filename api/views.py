from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView, status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from .serializers import *
from .models import *
from django.db.models import Sum, DecimalField
from datetime import date , datetime
import jdatetime
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

class CategoryListCreateAPIView(generics.ListCreateAPIView):
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

class TransactionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
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
    serializer_class = TransactionSerializer
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
    serializer_class = BudgetingSerializer

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
    serializer_class = BudgetingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budgeting.objects.select_related('category').filter(user=self.request.user)

    def preform_update(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({'detail': 'خطای دیتابیس هنگام اپدیت بودجه'})

class UserBalanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def calculate_balance(self, request):
        user = request.user
        total_income = (Transaction.objects.select_related('category', 'user').
                        filter(user=user, category__category_type='income')).aggregate(total=Sum('amount'))['total'] or 0

        total_expense = (Transaction.objects.select_related('category', 'user').
                        filter(user=user, category__category_type='expense')).aggregate(total=Sum('amount'))['total'] or 0

        final_balance = total_income - total_expense

        return total_income, total_expense, final_balance

    def get(self, request):
        #user = request.user
        total_income, total_expense, final_balance = self.calculate_balance(request)

        if final_balance < 0:
            final_balance_display = abs(final_balance)
            balance_status = 'تراز شما منفی است.'

        elif final_balance == 0:
            final_balance_display = 0
            balance_status = 'هزینه های شما با مخارج تان برابر بوده و حسابتان 0 است.'
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
        total_income, total_expense, final_balance = self.calculate_balance(request)

        confirm_saving = request.data.get('confirm_saving', False)

        if confirm_saving:

            if final_balance > 0:

                '''create_category = Category.objects.get_or_create(
                    user=user,
                    category_type='savings',
                    defaults={'name': 'پس‌انداز', 'color': 'سبز'})'''
                saving_category, created = Category.objects.get_or_create(user=user, category_type='savings',
                defaults={'name': 'پس انداز ', 'color':'سبز'})

                Transaction.objects.create(
                    user=user, amount=final_balance, category=saving_category,
                    description="پس‌انداز خودکار مازاد تراز مالی (ایجاد شده با مجوز کاربر)",
                    date=date.today()
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

class MonthlySummeryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        shamsi_year = request.query_params.get('year')
        shamsi_month = request.query_params.get('month')

        if not shamsi_year or not shamsi_month:
            return Response(
                {'detail': 'لطفا سال و ماه مورد نظر را مشخص کنید'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not 1300 <shamsi_year <1500 or not 1 <= shamsi_month <= 12:
            return Response(
                {'detail': 'لطفا سال و ماه معتبر وارد کنید'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            shamsi_year =int(shamsi_year)
            shamsi_month =int(shamsi_month)
            start_j_date = jdatetime.date(shamsi_year, shamsi_month, 1)
            start_gregorian_date = start_j_date.togregorian()

            if shamsi_month <= 6:
                end_day = 31
            elif shamsi_month <= 11:
                end_day = 30
            else:
                if jdatetime.date(shamsi_year,1 ,1).isleap():
                    end_day = 30
                else:
                    end_day = 29

            end_j_date = jdatetime.date(shamsi_year, shamsi_month, end_day)

            end_gregorian_date = end_j_date.togregorian()

        except ValueError:
            return Response(
                {"detail": "تاریخ وارد شده معتبر نیست."},
                status=status.HTTP_400_BAD_REQUEST
            )

        income_transactions = (Transaction.objects.select_related('category', 'user').
            filter(user=user, category__category_type='income', date__range=[start_gregorian_date, end_gregorian_date]))

        expense_transactions = (Transaction.objects.select_related('category', 'user').
                               filter(user=user, category__category_type='expense',
                                      date__range=[start_gregorian_date, end_gregorian_date]))

        monthly_total_income = income_transactions.aggregate(total=Sum('amount'))['total'] or 0

        monthly_total_expense = expense_transactions.aggregate(total=Sum('amount'))['total'] or 0

        monthly_average_income = monthly_total_income / end_day
        monthly_average_expense = monthly_total_expense / end_day

        month_num = {
            1:'فروردین', 2: 'اردیبیهشت', 3: 'خرداد', 4: 'تیر', 5: 'مرداد', 6: 'شهریور',
            7: 'مهر', 8: 'ابان', 9: 'اذر', 10: 'دی', 11: 'بهمن', 12: 'اسفند'
        }

        if monthly_total_expense == 0 and monthly_total_income == 0:
            message = f' شما تراکنشی در  {month_num[shamsi_month]} {shamsi_year}نداشته اید'
        else:
            message = f' مجموع تراکنش های شما در  ماه {month_num[shamsi_month]} {shamsi_year}'

        monthly_net_balance = monthly_total_income - monthly_total_expense

        return Response({
            'shamsi_year': shamsi_year,
            'shamsi_month': month_num[shamsi_month] ,
            'message': message,
            'total_income_monthly' : monthly_total_income,
            'total_expense_monthly': monthly_total_expense,
            'monthly_average_income': monthly_average_income,
            'monthly_average_expense': monthly_average_expense,
            'monthly_net_balance': monthly_net_balance
        },status=status.HTTP_200_OK)

class YearlySummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        shamsi_year = 1404#request.query_params.get('year')

        if not shamsi_year:
            return Response(
                {'detail': 'لطفا عدد سال مورد نظر خود را مشخص کنید'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not 1300 <shamsi_year <1500 :
            return Response(
                {'detail': 'لطفا سال معتبر وارد کنید'},
                status=status.HTTP_400_BAD_REQUEST
            )

        month_num = {
            1:'فروردین', 2: 'اردیبیهشت', 3: 'خرداد', 4: 'تیر', 5: 'مرداد', 6: 'شهریور',
            7: 'مهر', 8: 'ابان', 9: 'اذر', 10: 'دی', 11: 'بهمن', 12: 'اسفند'
        }

        all_months_summary = []

        for month in range(1,13):
            if month <= 6:
                end_day = 31
            elif month <= 11:
                end_day = 30
            else:
                if jdatetime.date(shamsi_year,1 ,1).isleap():
                    end_day = 30
                else:
                    end_day = 29
            start_j_date = jdatetime.date(shamsi_year, month, 1)
            end_j_date = jdatetime.date(shamsi_year, month, end_day)
            start_gregorian_date= start_j_date.togregorian()
            end_gregorian_date = end_j_date.togregorian()

            income_transactions = (Transaction.objects.select_related('category', 'user').
                                       filter(user=user, category__category_type='income',
                                              date__range=[start_gregorian_date, end_gregorian_date]))
            expense_transactions = (Transaction.objects.select_related('category', 'user').
                                    filter(user=user, category__category_type='expense',
                                           date__range=[start_gregorian_date, end_gregorian_date]))

            all_months_incomes = income_transactions.aggregate(total=Sum('amount'))['total'] or 0

            all_months_expenses = expense_transactions.aggregate(total=Sum('amount'))['total'] or 0

            all_months_summary.append({
                'month_num': month,
                'month_name': month_num[month],
                'all_months_incomes': all_months_incomes,
                'all_months_expenses': all_months_expenses,
            })

        try:
            shamsi_year = int(shamsi_year)
            start_j_date = jdatetime.date(shamsi_year, 1, 1)

            if jdatetime.date(shamsi_year, 1, 1).isleap():
                end_day = 30
            else:
                end_day = 29

            end_j_date = jdatetime.date(shamsi_year, 12, end_day)

            end_gregorian_date = end_j_date.togregorian()
            start_gregorian_date = start_j_date.togregorian()

        except ValueError:
            return Response(
                {"detail": "تاریخ وارد شده معتبر نیست."},
                status=status.HTTP_400_BAD_REQUEST
            )

        income_transactions = (Transaction.objects.select_related('category', 'user').
            filter(user=user, category__category_type='income', date__range=[start_gregorian_date, end_gregorian_date]))

        expense_transactions = (Transaction.objects.select_related('category', 'user').
                               filter(user=user, category__category_type='expense',
                                      date__range=[start_gregorian_date, end_gregorian_date]))

        yearly_total_income = income_transactions.aggregate(total=Sum('amount'))['total'] or 0

        yearly_total_expense = expense_transactions.aggregate(total=Sum('amount'))['total'] or 0

        if yearly_total_expense == 0 and yearly_total_income == 0:
            message = f'شما در سال{shamsi_year} تراکنشی نداشته اید'
        else:
            message = f'{shamsi_year} مجموع تراکنش های شما در سال '

        yearly_net_balance = yearly_total_income - yearly_total_expense

        return Response({
            'shamsi_year': shamsi_year,
            'message': message,
            'total_income_yearly' : yearly_total_income,
            'total_expense_yearly': yearly_total_expense,
            'yearly_net_balance': yearly_net_balance,
            'all_months_summary': all_months_summary


        },status=status.HTTP_200_OK)