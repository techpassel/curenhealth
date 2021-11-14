from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', views.DoctorView.as_view()),
    path('speciality/', views.SpecialityView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)