from pathlib import Path
import os, json
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from json import JSONDecodeError
import requests
from django.shortcuts import redirect

BASE_DIR = Path(__file__).resolve().parent.parent
secret_file = os.path.join(BASE_DIR, "secrets.json")

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

# KAKAO API용 정보
KAKAO_CLIENT_ID = get_secret("KAKAO_CLIENT_ID")
KAKAO_REDIRECT = get_secret("KAKAO_REDIRECT")
KAKAO_CLIENT_SECRET = get_secret("KAKAO_CLIENT_SECRET")

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
    
class Kakao_login(View):
    def get(self, request):
        kakao_api = "https://kauth.kakao.com/oauth/authorize?response_type=code"
        redirect_uri = KAKAO_REDIRECT
        client_id = KAKAO_CLIENT_ID

        return redirect(f"{kakao_api}&client_id={client_id}&redirect_uri={redirect_uri}&prompt=login")
    
class Kakao_callback(View):
    def get(self, request):
        error = request.GET.get("error")
        if error is not None:
            return JSONDecodeError(request.GET.get("error_description"))

        auth_code = request.GET.get("code")
        data = {
            "grant_type" : "authorization_code",
            "client_id" : KAKAO_CLIENT_ID,
            "redirection_uri" : KAKAO_REDIRECT,
            "code" : auth_code
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }

        kakao_token_api = f"https://kauth.kakao.com/oauth/token?client_secret={KAKAO_CLIENT_SECRET}"
        response = requests.post(kakao_token_api, data=data, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get("access_token")

            if access_token:
                return JsonResponse({"access_token" : access_token})
            else:
                return JsonResponse({"error" : "access_token not found"}, status=400)

        else:
            try:
                error_data = response.json()
            except ValueError:
                error_data = response.text

            return JsonResponse({"error": "Failed to obtain access token", "details": error_data}, status=response.status_code)
