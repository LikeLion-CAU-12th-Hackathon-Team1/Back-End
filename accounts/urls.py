from django.urls import path
from accounts.views import *

urlpatterns = [
    path('', hello_world, name = 'hello_world'),
]