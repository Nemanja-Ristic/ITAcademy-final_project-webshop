from os import name
from django.urls import path

from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    #path('product_view/', views.product_view, name="product_view"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name='logout'),
    path('register-user/', views.register, name='register'),
    #path('view_profile/', views.view_profile, name='view_profile'),
    path('checkout/', views.checkout, name="checkout"),
    path('<int:id>/', views.details, name='details'),
    path('update_item/', views.update_item, name="update_item"),
    path('process_order/', views.process_order, name="process_order"),
    
]
