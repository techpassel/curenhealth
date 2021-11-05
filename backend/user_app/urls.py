from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('user-details/', views.UserDetailsView.as_view()),
    path('delete-user/<int:user_id>', views.DeleteUserView.as_view()),
    path('update-user/', views.UpdateUserView.as_view()),
    path('update-password/', views.UpdatePasswordView.as_view()),
    path('update-email-request/', views.UpdateEmailRequestView.as_view()),
    path('update-email-verify/<str:verification_token>', views.UpdateEmailVerificationView.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)