from django.template.context_processors import request
from rest_framework import serializers
from .models import *
from django.db import IntegrityError

class CategorySerializer(serializers.ModelSerializer):
    #id = serializers.SlugRelatedField(read_only=True)
    #created_at = serializers.DateTimeField(read_only=True)
    #updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Category
        fields =[
            'id', 'name', 'category_type', 'color', 'default_amount', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at', 'id']

    def validate_name(self, value): #category name clean
        request = self.context.get('request') #getting request
        user = getattr(request, 'user', None) #getting user
        query_set = Category.objects.select_related('user').none()
        if user and user.is_authenticated:
            query_set  = Category.objects.select_related('user').filter(user=user, name=value)
            if user.instance:
                if query_set.exclude(pk=self.instance.pk) .exists():
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

class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ['id', 'user', 'category', 'amount', 'description',
                  'transaction_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value and value < 0:
            raise serializers.ValidationError('مبلع پیش فرض نمیتواند منفی باشد!')
