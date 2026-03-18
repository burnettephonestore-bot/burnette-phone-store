from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('updates/', views.updates_view, name='updates'),
    path('request/', views.request_product, name='request_product'),
    path('requests/', views.request_history, name='request_history'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:cart_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('sitemap.xml', views.sitemap, name='sitemap'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/request/<int:request_id>/status/<str:status>/', views.admin_update_request_status, name='admin_update_request_status'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    # API URLs
    path('api/products/', views.ProductListAPI.as_view(), name='api_products'),
    path('api/products/<int:pk>/', views.ProductDetailAPI.as_view(), name='api_product_detail'),
    path('api/updates/', views.UpdateListAPI.as_view(), name='api_updates'),
    path('api/cart/', views.CartListAPI.as_view(), name='api_cart'),
    path('api/cart/<int:pk>/', views.CartDetailAPI.as_view(), name='api_cart_detail'),
    path('api/profile/', views.UserProfileAPI.as_view(), name='api_profile'),
    path('api/request/', views.create_request_api, name='api_request'),
]