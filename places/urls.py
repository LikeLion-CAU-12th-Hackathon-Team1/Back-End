from .views import ListCreatePlace, CategoryPlace
from django.urls import path

urlpatterns = [
    path('', ListCreatePlace.as_view(), name='place-list'),
    path('<int:sigg_id>/', CategoryPlace.as_view(), name='category-places'),
]