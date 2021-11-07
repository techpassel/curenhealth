from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('login/', views.login, name="login"),
    path('activate-account/<str:token>', views.activate_account, name="activate-account"),
    path('resend-activation-email/', views.resend_activation_email, name="resend-activation-email"),
    path('forget-password/', views.forget_password, name="forget-password"),
    path('verify-reset-password-token/<str:token>', views.verify_reset_password_token, name="verify-reset-password-token"),
    path('reset-password/', views.reset_password, name="reset-passord")
]
