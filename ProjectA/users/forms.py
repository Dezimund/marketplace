from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils.html import strip_tags
from django.core.validators import RegexValidator

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
            'placeholder': 'Email'
        })
    )
    first_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
            'placeholder': "Ім'я"
        })
    )
    last_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
            'placeholder': 'Прізвище'
        })
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
            'placeholder': 'Пароль'
        })
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
            'placeholder': 'Підтвердіть пароль'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Цей email вже використовується')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = None
        if commit:
            user.save()
        return user


class CustomUserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
            'placeholder': 'Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
            'placeholder': 'Пароль'
        })
    )

    error_messages = {
        'invalid_login': 'Невірний email або пароль.',
        'inactive': 'Цей акаунт неактивний.',
    }

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
        return self.cleaned_data


class CustomUserUpdateForm(forms.ModelForm):
    phone_number = forms.CharField(
        required=False,
        validators=[
            RegexValidator(
                r'^(\+380|380|0)\d{9}$',
                'Введіть коректний номер телефону'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
            'placeholder': '+380XXXXXXXXX'
        })
    )
    first_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
            'placeholder': "Ім'я"
        })
    )
    last_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
            'placeholder': 'Прізвище'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
            'placeholder': 'Email'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'company',
                  'address1', 'address2', 'city', 'country', 'state',
                  'postal_code', 'phone_number')
        widgets = {
            'company': forms.TextInput(attrs={
                'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
                'placeholder': 'Компанія'
            }),
            'address1': forms.TextInput(attrs={
                'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
                'placeholder': 'Адреса (рядок 1)'
            }),
            'address2': forms.TextInput(attrs={
                'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
                'placeholder': 'Адреса (рядок 2)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
                'placeholder': 'Місто'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
                'placeholder': 'Країна'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
                'placeholder': 'Область'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control w-100 py-3 fs-6 fw-medium text-dark',
                'placeholder': 'Поштовий індекс'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Цей email вже використовується')
        return email

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('email'):
            cleaned_data['email'] = self.instance.email
        for field in ['company', 'address1', 'address2', 'city', 'country',
                      'state', 'postal_code', 'phone_number']:
            if cleaned_data.get(field):
                cleaned_data[field] = strip_tags(cleaned_data[field])
        return cleaned_data