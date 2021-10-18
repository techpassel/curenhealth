from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('change-password', views.change_password, name="change_password"),
    path('login', views.login, name="login")
]
