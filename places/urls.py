from .views import ListCreatePlace, CategoryPlace
from django.urls import path
from .views import SidoListCreateAPIView, SiggListCreateAPIView

urlpatterns = [
    path('', ListCreatePlace.as_view(), name='place-list'),
    path('work/<int:sigg_id>/', CategoryPlace.as_view(), name='category-places'),
    path('rest/<int:sigg_id>/', CategoryPlace.as_view(), name='category-places'),
]