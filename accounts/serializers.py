#from datetime import timezone
from rest_framework import serializers
from .models import AppUser, OTPCode
from .utils import generate_and_send_otp
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

"""if not AppUser.objects.filter(phone=value).exists():
        raise serializers.ValidationError()"""

class RequestOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11, required=True, help_text=' شماره موبایل 09xxxxxxxxx')

    def validate_phone(self, value):

        if not len(value) == 11:
            raise serializers.ValidationError('شماره موبایل باید دقیقا 11 رقم داشته باشد')
        if not value.startswith('09'):
            raise serializers.ValidationError('شماره موبایل باید با 09 آغاز شود')
        if not value.isdigit():
            raise serializers.ValidationError('شماره موبایل باید عددی باشد')

        return value

    @transaction.atomic
    def save(self):
        phone = self.validated_data['phone']

        user, created = AppUser.objects.get_or_create(
            phone=phone,
            defaults={}
        )
        generate_and_send_otp(user)

        return user, created

class VerifyOTPAndLoginCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11, required=True, help_text=' شماره موبایل 09xxxxxxxxx')
    code = serializers.CharField(max_length=6, required=True, help_text='کد ارسال شده')

    def validate(self, data):
        phone = data.get('phone')
        login_code = data.get('code')

        try:
            user = AppUser.objects.get(phone=phone)
        except AppUser.DoesNotExist:
            raise serializers.ValidationError('شماره موبایل وارد شده اشتباه است')

        try:
            otp_code = OTPCode.objects.get(user=user, code=login_code)
        except OTPCode.DoesNotExist:
            raise serializers.ValidationError('کد وارد شده اشتباه است')

        print(otp_code.code)

        if otp_code.expire_at < timezone.now():
            raise serializers.ValidationError('کد شما منقضی شده است')

        #if otp_code.code != login_code:
            #raise serializers.ValidationError('کد شما اشتباه است')

        otp_code.delete()

        #user = AppUser.objects.get(phone=phone)
        refresh = RefreshToken.for_user(user)

        data['user'] = user
        data['token'] = {'refresh': str(refresh), 'access': str(refresh.access_token)}

        return data


