from django.urls import path
from . import views

urlpatterns = [
    path('', views.app, name='app'),

    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.updateItem, name='update_item'),

    path('product/<int:id>/', views.product_detail, name='product_detail'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('wishlist/', views.wishlist, name='wishlist'),
    path('remove_from_wishlist/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('update_wishlist/', views.update_wishlist, name="update_wishlist"),
  


]

