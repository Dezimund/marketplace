from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'reviews'

router = DefaultRouter()
router.register(r'my-reviews', views.UserReviewsViewSet, basename='my-reviews')

urlpatterns = [
    path('products/<slug:product_slug>/reviews/',views.ReviewViewSet.as_view({'get': 'list','post': 'create',}),name='product-reviews'),
    path('products/<slug:product_slug>/reviews/stats/',views.ReviewViewSet.as_view({'get': 'stats'}),name='product-reviews-stats'),
    path('products/<slug:product_slug>/reviews/my/',views.ReviewViewSet.as_view({'get': 'my'}),name='product-reviews-my'),
    path('products/<slug:product_slug>/reviews/<int:pk>/',views.ReviewViewSet.as_view({'get': 'retrieve','put': 'update','patch': 'partial_update','delete': 'destroy', }),name='product-review-detail'),
    path('products/<slug:product_slug>/reviews/<int:pk>/helpful/',views.ReviewViewSet.as_view({'post': 'helpful'}),name='product-review-helpful'),
    path('', include(router.urls)),
]