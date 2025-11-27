import random
from django.utils import timezone
from datetime import timedelta
from .models import OTPCode

def generate_and_send_otp(user):
    new_code = str(random.randint(100000, 999999))
    expiration_time = timezone.now() + timedelta(minutes=2)
    OTPCode.objects.filter(expire_at__gt=timezone.now()).delete()

    otp_instance= OTPCode.objects.create(
        user=user, code=new_code, expire_at=expiration_time
    )

    return otp_instance