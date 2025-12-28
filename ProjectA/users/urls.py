from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile-view/', views.profile_view, name='profile_view'),
    path('account-details/', views.account_details, name='account_details'),
    path('edit-account-details/', views.edit_account_details, name='edit_account_details'),
    path('update-account-details/', views.update_account_details, name='update_account_details'),
    path('logout/', views.logout, name='logout'),
]