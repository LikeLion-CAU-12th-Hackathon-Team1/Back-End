from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

class IsAuthenticatedAndReturnUser(IsAuthenticated):
    def has_permission(self, request, view):
        # IsAuthenticated 권한 확인.
        is_authenticated = super().has_permission(request, view)
        if not is_authenticated:
            return False

        # JWT 토큰으로 사용자 인증.
        jwt_authenticator = JWTAuthentication()
        try:
            # Authorization 헤더에서 토큰 추출.
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return False

            # Bearer 토큰으로 추출.
            token = auth_header.split()[1] if auth_header.startswith('Bearer') else None
            if not token:
                return False

            # 토큰 검증, 사용자 객체를 요청 객체에 설정.
            validated_token = jwt_authenticator.get_validated_token(token)
            request.user = jwt_authenticator.get_user(validated_token)
            return True
        except AuthenticationFailed:
            return False
        except Exception:
            return False    

# class IsOwnerOrReadOnly(BasePermission):
#     def has_object_permission(self, request, view, obj):
#         if request.method in SAFE_METHODS:
#             return True
#         return request.user == obj.owner

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner
