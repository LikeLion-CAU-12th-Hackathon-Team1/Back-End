from django.urls import path
from oauths.views import *

urlpatterns = [
    path('', Kakao_callback.as_view(), name = 'login'),
]