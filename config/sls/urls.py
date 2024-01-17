from django.urls import path
from . import views

urlpatterns = [
    path('account/register/', views.register, name='register'),
    path('', views.index, name='index'),
    path('account/logout/', views.logout_view, name='logout'),
    path('transfer/', views.transfer, name='transfer'),
    path('transfer_history/', views.transfer_history, name='transfer_history'),
    path('personal_info/', views.personal_info, name='personal_info')
]
