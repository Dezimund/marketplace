from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('', views.RecommendationsAPIView.as_view(), name='recommendations'),
    path('home/', views.PersonalizedHomeAPIView.as_view(), name='personalized-home'),
]