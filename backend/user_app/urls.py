from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('userdetails/', views.UserDetailsView.as_view()),
    path('userdetails/<int:user_id>', views.GetUserDetailsView.as_view()),
    path('delete-userdetails/<int:id>', views.DeleteUserDetailsView.as_view()),
    path('delete-user/<int:user_id>', views.DeleteUserView.as_view()),
    path('update-user/', views.UpdateUserView.as_view()),
    path('update-password/', views.UpdatePasswordView.as_view()),
    path('update-email-request/', views.UpdateEmailRequestView.as_view()),
    path('update-email-verify/<str:token>', views.UpdateEmailVerificationView.as_view()),
    path('health-record/', views.HealthRecordsView.as_view()),
    path('health-record/<int:user_id>', views.GetHealthRecordsView.as_view()),
    path('delete-health-record/<int:id>', views.DeleteHealthRecordsView.as_view()),
    path('subscription-schemes/', views.GetAllSubscriptionSchemesView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)