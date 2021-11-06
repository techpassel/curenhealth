from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('login/', views.login, name="login"),
    path('activate-account/<str:token>', views.activate_account, name="activate_account"),
    path('resend-activation-email/', views.resend_activation_email, name="resend_activation_email"),
    path('forget-password/', views.forget_password, name="forget-password"),
    path('reset-password/', views.reset_password, name="reset-passord")
]
