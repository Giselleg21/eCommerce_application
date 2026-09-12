from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', TemplateView.as_view(
        template_name='Shop/home.html'), name='home'),
    path('login/', views.CustomLoginView.as_view(
        template_name='Shop/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('products/', views.product_list, name='product_list'),
    path('stores/', views.store_list, name='store_list'),
    path('product/<int:product_id>/',
         views.product_detail, name='product_detail'),
    path('store/<int:store_id>/', views.store_detail, name='store_detail'),
    path('product/new/', views.product_create, name='product_create'),
    path('product/<int:product_id>/delete/',
         views.product_delete, name='product_delete'),
    path('product/<int:product_id>/edit',
         views.product_update, name='product_update'),
    path('store/new', views.store_create, name='store_create'),
    path('store/<int:store_id>/delete/',
         views.store_delete, name='store_delete'),
    path('store/<int:store_id>/edit',
         views.store_update, name='store_update'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/',
         views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('invoice/<int:order_id>/', views.invoice, name='invoice'),
    path('product/<int:product_id>/review/',
         views.review_create, name='review_create'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='Shop/password_reset.html'), name='password_reset'),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='Shop/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='Shop/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='Shop/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    path("reddit/", views.reddit_feed, name="reddit_feed"),
    path('api/stores/create/', views.api_create_store,
         name='api_create_store'),
    path('api/products/create/', views.api_create_product,
         name='api_create_product'),
    path('api/stores/', views.api_store_list,
         name='api_store_list'),
    path('api/stores/<int:store_id>/products/',
            views.api_store_products,
            name='api_store_products'),
    path('api/stores/<int:store_id>/reviews/',
            views.api_store_reviews,
            name='api_store_reviews'),
    ]
