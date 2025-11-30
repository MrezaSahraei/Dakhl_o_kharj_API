from django.template.context_processors import request
from rest_framework import serializers
from .models import *
from django.db import IntegrityError
import jdatetime
class CategorySerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    user_full_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Category
        fields =[
            'id', 'name','user', 'user_full_name','category_type',
            'color', 'default_amount', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'id', 'user', 'user_full_name']

    def validate_name(self, value): #category name clean
        request = self.context.get('request') #getting request
        user = getattr(request, 'user', None) #getting user
        query_set = Category.objects.select_related('user').none()
        if user and user.is_authenticated:
            query_set = Category.objects.select_related('user').filter(user=user, name=value)
            if self.instance:
                if query_set.exclude(pk=self.instance.pk).exists():
                    raise serializers.ValidationError('از قبل دسته ای با این نام دارید!')
        return value

    def validate_default_amount(self, value): #default_amount clean
        if value and value < 0:
            raise serializers.ValidationError('مبلع پیش فرض نمیتواند منفی باشد!')
        return value

    def create(self,validated_data):
        request = self.context.get('request') #getting request
        user = getattr(request, 'user', None)
        vd = validated_data
        try: # مدیریت خطای دیتابیس هنگام ساخت رکورد جدید
            instance = Category.objects.create(user=user,
                name=vd['name'],
                category_type=vd['category_type'],
                color=vd['color'],
                default_amount=vd['default_amount'],
                is_active=vd['is_active'])
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'خطای دیتابیس بخاطر رکورد تکراری یا نقض محدودیت '})
        return instance

    def update(self, instance, validate_data):
        validate_data.pop('user',None) #Preventing the client from changing the user
        for attr, value in validate_data.items():
            setattr(instance, attr, value)
        try: #مدیریت حطای دیتابیس هنگام اپدیت رکورد
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'خطای دیتابیس هنگام اپدیت دسته'})
        return instance

    def get_user(self,obj):
       return obj.user.phone

    def get_user_full_name(self,obj):
        if obj.user.first_name and obj.user.last_name:
            return obj.user.first_name, obj.user.last_name
        return None

class TransactionSerializer(serializers.ModelSerializer):

    shamsi_year = serializers.IntegerField(min_value=1330, max_value=1500, write_only=True, required=True)
    shamsi_month = serializers.IntegerField(min_value=1, max_value=12, write_only=True, required=True)
    shamsi_day = serializers.IntegerField(min_value=1, max_value=31, write_only=True, required=True)

    shamsi_date = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['id', 'user', 'category', 'amount',
                  'description', 'date', 'created_at',
                  'updated_at', 'shamsi_year', 'shamsi_month', 'shamsi_day', 'shamsi_date'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'date']

    def validate_amount(self, value):
        if value and value < 0:
            raise serializers.ValidationError('مبلع پیش فرض نمیتواند منفی باشد!')
        return value

    def validate_category(self, value):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and value.user.id != getattr(user, 'id', None):
            raise serializers.ValidationError('دسته انتخاب شده متعلق به شما نیست')
        if value is None:
            raise serializers.ValidationError('دسته ای انتخاب نشده است!')
        if not value.is_active:
            raise serializers.ValidationError('نمیتوانید تراکنشی داشته باشید زیرا این دسته غیرفغال است')
        return value

    def create(self,validated_data):
        request = self.context.get('request') #getting request
        user = getattr(request, 'user', None)
        shamsi_year = validated_data.pop('shamsi_year')
        shamsi_month = validated_data.pop('shamsi_month')
        shamsi_day =  validated_data.pop('shamsi_day')
        try:
            jdate_object = jdatetime.date(shamsi_year, shamsi_month, shamsi_day)
            gregorian_date = jdate_object.togregorian()
            validated_data['date'] = gregorian_date
        except ValueError:
            raise serializers.ValidationError({'detail':'تاریخ وارد شده نامعتبر است'})
        vd = validated_data
        try: # مدیریت خطای دیتابیس هنگام ساخت رکورد جدید
            instance = Transaction.objects.create(user=user,
                category=vd['category'],
                amount=vd['amount'],
                description=vd.get('description'),
                date=validated_data['date'],
                record_date=vd['record_date'])
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'خطای دیتابیس هنگام ثبت تراکنش '})
        return instance

    def update(self, instance, validated_data):
        validated_data.pop('user', None) #Preventing the client from changing the user in transactions
        shamsi_year = validated_data.pop('shamsi_year')
        shamsi_month = validated_data.pop('shamsi_month')
        shamsi_day =  validated_data.pop('shamsi_day')
        jdate_object = jdatetime.date(shamsi_year, shamsi_month, shamsi_day)
        gregorian_date = jdate_object.togregorian()
        validated_data['date'] = gregorian_date


        for attr , value in validated_data.items():
            setattr(instance, attr, value)
        try:
            instance.save()

        except IntegrityError:
            raise serializers.ValidationError({'detail': 'خطای دیتابیس هنگام اپدیت تراکنش'})
        return instance

    def get_shamsi_date(self, obj):
        jdate_object = jdatetime.date.fromgregorian(date=obj.date)
        return jdate_object.strftime("%Y/%m/%d")

    def get_user(self,obj):
       return obj.user.phone

class BudgetingSerializer(serializers.ModelSerializer):

    shamsi_year_start = serializers.IntegerField(min_value=1403, max_value=1500, write_only=True, required=True)
    shamsi_month_start = serializers.IntegerField(min_value=1, max_value=12, write_only=True, required=True)
    shamsi_day_start = serializers.IntegerField(min_value=1, max_value=31, write_only=True, required=True)

    shamsi_year_end = serializers.IntegerField(min_value=1403, max_value=1500, write_only=True, required=True)
    shamsi_month_end = serializers.IntegerField(min_value=1, max_value=12, write_only=True, required=True)
    shamsi_day_end = serializers.IntegerField(min_value=1, max_value=31, write_only=True, required=True)

    shamsi_start = serializers.SerializerMethodField()
    shamsi_end = serializers.SerializerMethodField()

    class Meta:
        model = Budgeting
        fields = [
            'id','category', 'minimum_target_amount', 'maximum_target_amount',
        'start_date','shamsi_year_start', 'shamsi_month_start' ,'shamsi_day_start',
            'end_date','shamsi_year_end','shamsi_month_end','shamsi_day_end','shamsi_start','shamsi_end',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_category(self, value):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and value.user.id != getattr(user, 'id', None):
            raise serializers.ValidationError('دسته انتخاب شده متعلق به شما نیست')
        if value is None:
            raise serializers.ValidationError('دسته ای انتخاب نشده است!')
        return value

    def validate(self, data):
        """
        General checks: start <= end and min <= max and ensuring non-negative values
        """
        def get_final_value(field_name): #for PATCH requests
            new_value = data.get(field_name)

            if new_value is None and self.instance:
                return getattr(self.instance, field_name, None)
            return new_value

        #getting fields from data
        min_amt = data.get('minimum_target_amount')
        max_amt = data.get('maximum_target_amount')

        start_year = data.get('shamsi_year_start')
        start_month = data.get('shamsi_month_start')
        start_day = data.get('shamsi_day_start')

        end_year = data.get('shamsi_year_end')
        end_month = data.get('shamsi_month_end')
        end_day = data.get('shamsi_day_end')

        try:
            jdate_start = jdatetime.date(start_year, start_month, start_day)
            jdate_end = jdatetime.date(end_year, end_month, end_day)
            data['start_date']= jdate_start.togregorian()
            data['end_date'] = jdate_end.togregorian()
        except ValueError:
            raise serializers.ValidationError({'detail': 'تاریخ وارد شده معتبر نیست'})

        start = data['start_date']
        end = data['end_date']

        if min_amt and max_amt and min_amt > max_amt:
            raise serializers.ValidationError('حداکثر بودجه تعیین شده نمیتواند کوچکتر از حداقل بودجه تعیین شده باشد ')

        if min_amt and max_amt and min_amt == max_amt:
            raise serializers.ValidationError('حداکثر بودجه تعیین شده نمیتواند برابر با حداقل بودجه تعیین شده باشد ')

        if (min_amt is not None) and min_amt < 0 or (max_amt is not None) and max_amt < 0:
            raise serializers.ValidationError('مبلع بودجه نمیتواند منفی باشد!')

        if start and end and start > end:
            raise serializers.ValidationError('تارخ پایان نمیتواند کوچکتر از تاریخ شروع باشد')

        if start and end and start == end:
            raise serializers.ValidationError('تارخ پایان نمیتواند برابر با تاریخ شروع باشد')

        return data

    def create(self, validated_data):
        request =self.context.get('request')
        user = getattr(request, 'user', None)
        vd = validated_data

        try: # مدیریت خطای دیتابیس هنگام ساخت رکورد جدید
            instance = Budgeting.objects.create(user=user,
                category=vd['category'],
                minimum_target_amount=vd['minimum_target_amount'],
                maximum_target_amount=vd['maximum_target_amount'],
                start_date=vd['start_date'], end_date=['end_date'])
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'خطای دیتابیس هنگام ثبت بودجه '})
        return instance

    def update(self, instance, validated_data):
        validated_data.pop('user', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value )
        try:
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'خطای دیتابیس هنگام اپدیت بودجه '})
        return instance

    def get_shamsi_start(self, obj):
        jdate_object = jdatetime.date.fromgregorian(date=obj.start_date)
        return jdate_object.strftime("%Y/%m/%d")

    def get_shamsi_end(self, obj):
        jdate_object = jdatetime.date.fromgregorian(date=obj.end_date)
        return jdate_object.strftime("%Y/%m/%d")
