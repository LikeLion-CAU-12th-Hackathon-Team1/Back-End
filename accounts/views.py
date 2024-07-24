from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from json import JSONDecodeError
import requests
# from django.shortcuts import redirect
# from config.settings import get_secret

# KAKAO_CLIENT_ID = get_secret("KAKAO_CLIENT_ID")
# KAKAO_REDIRECT = get_secret("KAKAO_REDIRECT")

def hello_world(request):
    if request.method == "GET":
        return JsonResponse({
            'status' : 200,
            'data' : 'Hello 생활체육인!!'
        })

    if request.method == "POST":
        return JsonResponse({
            'status' : 200,
            'data' : 'post message success'
        })
    
# class Kakao_login(View):
#     def get(self, request):
#         kakao_api = "https://kauth.kakao.com/oauth/authorize?response_type=code"
#         redirect_uri = KAKAO_REDIRECT
#         client_id = KAKAO_CLIENT_ID

#         return redirect(f"{kakao_api}&client_id={client_id}&redirect_uri={redirect_uri}&prompt=login")
