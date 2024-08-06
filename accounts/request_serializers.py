from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework import serializers
from .models import User

class RegisterLoginSerializer(serializers.ModelSerializer):
    kakao_id = serializers.IntegerField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['kakao_id', 'email']

    def save(self, request):
        user = User.objects.create(
            kakao_id = str(self.validated_data['kakao_id']),
            email = self.validated_data['email']
        )

        return user

class UserNicknameSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['nickname']

    def update(self, instance, validated_data):
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.save()
        return instance
