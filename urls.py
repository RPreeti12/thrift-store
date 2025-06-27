from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('index/', views.index, name='index'),
    path('', views.user_login, name="login"),
    path('register/', views.user_register, name='register'),
    path('dashboard/', views.seller_dashboard, name='dashboard'),  # Seller dashboard
    path('add-product/', views.add_product, name='add_product'),  # Add product page
    path('view-products/', views.view_seller_products, name='view_products'),  # View Products URL
    path('edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('seller_profile/', views.seller_profile, name='seller_profile'),
    path('logout/', views.logout, name='logout'),  # Redirect to homepage after logout
    path('cart/',views.cart,name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name="add_to_cart"),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name="remove_from_cart"),
    path('buy_now/', views.buy_now, name='buy_now'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

   

