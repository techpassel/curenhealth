from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', views.DoctorView.as_view()),
    path('<int:id>', views.GetDoctorDetails.as_view()),
    path('search-doctors/', views.SearchDoctors.as_view()),
    path('speciality/', views.SpecialityView.as_view()),
    path('consultation/', views.ConsultationView.as_view()),
    path('search-consultation/', views.SearchConsultations.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)