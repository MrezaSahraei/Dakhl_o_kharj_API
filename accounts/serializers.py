from rest_framework import serializers
from .models import AppUser
from .utils import generate_and_send_otp
from django.db import transaction

"""if not AppUser.objects.filter(phone=value).exists():
        raise serializers.ValidationError()"""

class VerifyOTPAndLoginCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11, required=True, help_text=' شماره موبایل 09xxxxxxxxx')

    def validate_phone(self, value):
        if len(value) < 11:
            raise serializers.ValidationError('شماره موبایل باید 11 رقم داشته باشد')
        if not value.startwith('09'):
            raise serializers.ValidationError('شماره موبایل باید با 09 آغاز شود')
        if not value.isdigit():
            raise serializers.ValidationError('شماره موبایل باید عددی باشد')

    @transaction.atomic
    def save(self):
        phone = self.validated_data['phone']

        user, created = AppUser.objects.get_or_create(
            phone=phone,
            defaults={}
        )
        generate_and_send_otp(user)

        return user, created
