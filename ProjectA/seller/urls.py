from django.urls import path
from .views import SellerDashboardView, SellerProductListView, SellerProductCreateView, SellerProductUpdateView, SellerProductDeleteView, SellerProductImageDeleteView


app_name = 'seller'

urlpatterns = [
    path('', SellerDashboardView.as_view(), name='dashboard'),
    path('products/', SellerProductListView.as_view(), name='product_list'),
    path('products/create/', SellerProductCreateView.as_view(), name='product_create'),
    path('products/<slug:slug>/edit/', SellerProductUpdateView.as_view(), name='product_edit'),
    path('products/<slug:slug>/delete/', SellerProductDeleteView.as_view(), name='product_delete'),
    path('images/<int:image_id>/delete/', SellerProductImageDeleteView.as_view(), name='image_delete'),
]