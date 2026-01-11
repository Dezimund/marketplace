from django import forms
from django.utils.html import strip_tags


class OrderForm(forms.Form):

    first_name = forms.CharField(
        max_length=50,
        label="Ім'я",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Ім'я"
        })
    )
    last_name = forms.CharField(
        max_length=50,
        label='Прізвище',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Прізвище'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'readonly': 'readonly'
        })
    )
    company = forms.CharField(
        max_length=100,
        required=False,
        label='Компанія',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Компанія (опціонально)'
        })
    )
    address1 = forms.CharField(
        max_length=255,
        required=False,
        label='Адреса',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Вулиця, будинок'
        })
    )
    address2 = forms.CharField(
        max_length=255,
        required=False,
        label='Адреса (додатково)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Квартира, офіс (опціонально)'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        label='Місто',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Місто'
        })
    )
    country = forms.CharField(
        max_length=100,
        required=False,
        label='Країна',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Країна'
        })
    )
    state = forms.CharField(
        max_length=100,
        required=False,
        label='Область',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Область'
        })
    )
    postal_code = forms.CharField(
        max_length=20,
        required=False,
        label='Поштовий індекс',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Індекс'
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label='Телефон',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+380 XX XXX XX XX'
        })
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

            if hasattr(user, 'company'):
                self.fields['company'].initial = getattr(user, 'company', '')
            if hasattr(user, 'address1'):
                self.fields['address1'].initial = getattr(user, 'address1', '')
            if hasattr(user, 'address2'):
                self.fields['address2'].initial = getattr(user, 'address2', '')
            if hasattr(user, 'city'):
                self.fields['city'].initial = getattr(user, 'city', '')
            if hasattr(user, 'country'):
                self.fields['country'].initial = getattr(user, 'country', '')
            if hasattr(user, 'state'):
                self.fields['state'].initial = getattr(user, 'state', '')
            if hasattr(user, 'postal_code'):
                self.fields['postal_code'].initial = getattr(user, 'postal_code', '')
            if hasattr(user, 'phone_number'):
                self.fields['phone_number'].initial = getattr(user, 'phone_number', '')

    def clean(self):
        cleaned_data = super().clean()

        text_fields = [
            'company', 'address1', 'address2', 'city',
            'country', 'state', 'postal_code', 'phone_number'
        ]
        for field in text_fields:
            if cleaned_data.get(field):
                cleaned_data[field] = strip_tags(cleaned_data[field])

        return cleaned_data