from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from json import JSONDecodeError
import requests
from django.shortcuts import redirect
from config.settings import get_secret
from .request_serializers import RegisterLoginSerializer, UserNicknameSerializer
from .models import User
from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from config.permissions import IsAuthenticatedAndReturnUser

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
    permission_classes = [AllowAny]
    def get(self, request):
        kakao_api = "https://kauth.kakao.com/oauth/authorize?response_type=code"
        redirect_uri = KAKAO_REDIRECT
        client_id = KAKAO_CLIENT_ID

        return redirect(f"{kakao_api}&client_id={client_id}&redirect_uri={redirect_uri}&prompt=login")

class Kakao_callback(View):
    permission_classes = [AllowAny]
    def get(self, request):
        auth_code = request.GET.get("code")
        data = {
            "grant_type" : "authorization_code",
            "client_id" : KAKAO_CLIENT_ID,
            "redirection_uri" : KAKAO_REDIRECT,
            "code" : auth_code,
            'client_secret': KAKAO_CLIENT_SECRET
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }

        kakao_token_api = "https://kauth.kakao.com/oauth/token"
        response = requests.post(kakao_token_api, data=data, headers=headers)

        if response.status_code != 200:
            return JsonResponse({"error" : "access_token not found"}, status=400)
        
        response_data = response.json()
        access_token = response_data.get("access_token")

        if access_token:
            kakao_user_api = "https://kapi.kakao.com/v2/user/me"
            headers = {
                "Authorization": f"Bearer {access_token}",
                'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
            }
            response = requests.get(kakao_user_api, headers=headers)
            response_json = response.json()

            serialize_data = {
                'kakao_id' : response_json.get('id'),
                'name' : response_json.get('kakao_account').get('name'),
                'email' : response_json.get('kakao_account').get('email')
            }

            serializer = RegisterLoginSerializer(data=serialize_data)

            if serializer.is_valid():
                user = User.get_user_or_none_by_kakao_id(serializer.validated_data['kakao_id'])
                if user is None:
                    user = serializer.save(request)

                if user.profile != response_json.get('properties').get('profile_image'):
                    user.profile = response_json.get('properties').get('profile_image')
                    user.save()

                if user.nickname == "":
                    user.nickname = response_json.get('properties').get('nickname')
                    user.save()

                token = RefreshToken.for_user(user)
                refresh_token = str(token)
                access_token = str(token.access_token)
                res = JsonResponse({
                    "status" : 200,
                    "refresh_token" : refresh_token,
                    "access_token" : access_token,
                    "user" : {
                        "name" : user.name,
                        "nickname" : user.nickname,
                        "email" : user.email,
                        "profile" : user.profile
                    }
                })

                return res
            else:
                return JsonResponse({
                    "status" : 400,
                    "error" : "Failed to obtain access token"
                })

        else:
            try:
                error_data = response.json()
            except ValueError:
                error_data = response.text

            return JsonResponse({"error": "Failed to obtain access token", "details": error_data}, status=response.status_code)

class UserNickname(APIView):
    permission_classes = [IsAuthenticatedAndReturnUser]

    def patch(self, request):
        self.check_permissions(request)
        user = request.user
        serializer = UserNicknameSerializer(user, data=request.data, partial=True)  
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
