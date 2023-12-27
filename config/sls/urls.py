from django.urls import path
from . import views

urlpatterns = [
    path('account/register/', views.register, name='register'),
    path('', views.index, name='index'),
    path('account/logout/', views.logout_view, name='logout'),
]
