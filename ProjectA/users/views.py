from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .forms import CustomUserUpdateForm, CustomUserLoginForm, CustomUserCreationForm
from .models import CustomUser
from django.contrib import messages
from main.models import Product


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Реєстрація успішна! Ласкаво просимо!')
            return redirect('main:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login(request):
    if request.user.is_authenticated:
        return redirect('main:index')

    if request.method == 'POST':
        form = CustomUserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Ласкаво просимо, {user.first_name}!')

            next_url = request.GET.get('next', 'main:index')
            return redirect(next_url)
    else:
        form = CustomUserLoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required(login_url='/users/login/')
def profile_view(request):
    recommended_products = Product.objects.all().order_by('-views_count')[:3]

    user_products = None
    if request.user.is_seller:
        user_products = Product.objects.filter(seller=request.user).order_by('-created_at')[:5]

    context = {
        'form': CustomUserUpdateForm(instance=request.user),
        'user': request.user,
        'recommended_products': recommended_products,
        'user_products': user_products,
    }

    return TemplateResponse(request, 'users/profile.html', context)


@login_required(login_url='/users/login/')
def account_details(request):
    return TemplateResponse(request, 'users/account_details.html', {'user': request.user})


@login_required(login_url='/users/login/')
def edit_account_details(request):
    form = CustomUserUpdateForm(instance=request.user)
    return TemplateResponse(request, 'users/edit_account_details.html', {
        'user': request.user,
        'form': form
    })


@login_required(login_url='/users/login/')
def update_account_details(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.clean()
            user.save()

            updated_user = CustomUser.objects.get(id=user.id)

            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'users/account_details.html', {'user': updated_user})

            messages.success(request, 'Дані профілю успішно оновлено!')
            return redirect('users:profile_view')
        else:
            return TemplateResponse(request, 'users/edit_account_details.html', {
                'user': request.user,
                'form': form
            })

    if request.headers.get('HX-Request'):
        return HttpResponse(headers={'HX-Redirect': reverse('users:profile_view')})
    return redirect('users:profile_view')


def logout(request):
    if request.method == 'POST':
        auth_logout(request)
        messages.info(request, 'Ви вийшли з акаунту')

        if request.headers.get('HX-Request'):
            return HttpResponse(headers={'HX-Redirect': reverse('main:index')})
        return redirect('main:index')

    return render(request, 'users/logout.html')