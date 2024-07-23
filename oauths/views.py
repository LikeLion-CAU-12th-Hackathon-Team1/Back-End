from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import requests
from django.views import View
from config.settings import get_secret

# KAKAO API용 정보
KAKAO_CLIENT_ID = get_secret("KAKAO_CLIENT_ID")
KAKAO_REDIRECT = get_secret("KAKAO_REDIRECT")
KAKAO_CLIENT_SECRET = get_secret("KAKAO_CLIENT_SECRET")

class Kakao_callback(View):
    def get(self, request):
        # 프론트에서 요청 보낼 때 error 코드를 보내는 경우 대비 예외 처리 코드
        # error = request.GET.get("error")
        # if error is not None:
        #     return JSONDecodeError(request.GET.get("error_description"))

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
    
