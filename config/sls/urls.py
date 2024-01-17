from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('account/register/', views.register, name='register'),
    path('', views.index, name='index'),
    path('account/logout/', views.logout_view, name='logout'),
    path('account/change_password/', views.change_password, name='change_password'),
    path('account/reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('account/reset_password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('account/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('account/reset_password/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('transfer/', views.transfer, name='transfer'),
    path('transfer_history/', views.transfer_history, name='transfer_history'),
    path('profile/', views.profile, name='profile'),
    path('profile/<int:show_secrets>/', views.profile, name='profile')
]
