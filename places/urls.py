from .views import ListCreatePlace, CategoryPlace
from django.urls import path
from .views import SidoListCreateAPIView, SiggListCreateAPIView

urlpatterns = [
    path('', ListCreatePlace.as_view(), name='place-list'),
    path('<int:sigg_id>/', CategoryPlace.as_view(), name='category-places'),
    path('sido/', SidoListCreateAPIView.as_view(), name='sido-list-create'),
    path('sigg/', SiggListCreateAPIView.as_view(), name='sigg-list-create'),
]