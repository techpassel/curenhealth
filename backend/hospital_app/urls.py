from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('city/', views.CityView.as_view()),
    path('address/', views.AddressView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)