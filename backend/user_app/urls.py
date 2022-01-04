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
    path('user-subscription/', views.UserSubscriptionView.as_view()),
    path('user-subscription/<int:id>', views.GetUserSubscriptionDetailsView.as_view()),
    path('user-subscriptions/<int:user_id>', views.GetUsersAllSubscriptionView.as_view()),
    path('activate-user-subscription/', views.ActivateUserSubscription.as_view()),
    path('appointment/', views.AppointmentView.as_view()),
    path('appointment-by-doctor/<int:doctor_id>', views.GetAppointmentsByDoctorView.as_view()),
    path('appointment-by-user/<int:user_id>', views.GetAppointmentsByUserView.as_view()),
    path('delete-appointment/<int:id>', views.DeleteAppointmentView.as_view()),
    path('prescription/', views.PrescriptionView.as_view()),
    path('prescription-by-appointment/<int:appointment_id>', views.GetPrescriptionsByAppointmentView.as_view()),
    path('delete-prescription/<int:id>', views.DeletePrescriptionView.as_view()),
    path('delete-prescription-document/<int:id>', views.DeletePrescriptionDocumentView.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)