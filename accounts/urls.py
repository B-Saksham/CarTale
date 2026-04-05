from django.urls import path
from django.contrib.auth import views as auth_views
from .views import post_login_redirect, register

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html'
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('redirect/', post_login_redirect, name='post_login_redirect'),

    path('register/', register, name='register'),

]
