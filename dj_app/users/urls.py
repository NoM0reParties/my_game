from django.urls import path

from users import views

urlpatterns = [
    path('login', views.user_login, name='login'),
    path('register', views.user_register, name='register'),
    path('logout', views.user_logout, name='logout'),
    path('check_logged', views.check_logged, name='check_logged'),
]