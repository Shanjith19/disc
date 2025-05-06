from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/nearby-discounts/', views.nearby_discounts_api, name='nearby_discounts_api'),
    path('add-to-cart/<int:discount_id>/', views.add_to_cart, name='add_to_cart'),
    path('view-cart/', views.view_cart, name='view_cart'),
    path('payment/', views.process_payment, name='process_payment'),
    path('upload-discount/', views.upload_discount, name='upload_discount'),
    path('add-to-cart/<int:discount_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('approve-payment/<int:payment_id>/', views.approve_payment, name='approve_payment'),
    path('payment/', views.process_payment, name='process_payment'),
]
