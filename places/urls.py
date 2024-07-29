from .views import ListCreatePlace
from django.urls import path

urlpatterns = [
    path('', ListCreatePlace.as_view(), name='place-list'),
]