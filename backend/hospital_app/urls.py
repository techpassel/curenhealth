from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', views.HospitalView.as_view()),
    path('city/', views.CityView.as_view()),
    path('address/', views.AddressView.as_view()),
    path('get-address/<int:id>', views.GetAddressView.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)