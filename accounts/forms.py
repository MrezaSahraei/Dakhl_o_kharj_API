from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import AppUser

class ShopUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = AppUser
        fields = ('phone', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if AppUser.objects.filter(phone=phone).exists():
                raise forms.ValidationError('این شماره موبایل قبلا استفاده شده.')

        if not phone.isdigit():
                raise forms.ValidationError('شماره موبایل باید عددی باشد.')

        if not phone.startswith('09'):
                raise forms.ValidationError('شماره موبایل با 09xxxxxxxxx آغاز شود.')

        if len(phone) != 11:
                raise forms.ValidationError('شماره موبایل باید 11 رقم داشته باشد.')

        return phone


class ShopUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = AppUser
        fields = ('phone', 'first_name', 'last_name', 'address', 'is_active', 'is_staff', 'is_superuser')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if self.instance.pk:
            if AppUser.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('این شماره موبایل قبلا استفاده شده.')

        else:
            if AppUser.objects.filter(phone=phone).exists():
                raise forms.ValidationError('این شماره موبایل قبلا استفاده شده.')

        if not phone.isdigit():
            raise forms.ValidationError('شماره موبایل باید عددی باشد.')

        if not phone.startswith('09'):
            raise forms.ValidationError('شماره موبایل با 09xxxxxxxxx آغاز شود.')

        if len(phone) != 11:
            raise forms.ValidationError('شماره موبایل باید 11 رقم داشته باشد.')

        return phone




