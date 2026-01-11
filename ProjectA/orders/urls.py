from django.urls import path
from .views import CheckoutView, OrderHistoryView, OrderDetailView

app_name = 'orders'

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('history/', OrderHistoryView.as_view(), name='history'),
    path('<int:order_id>/', OrderDetailView.as_view(), name='detail'),
]