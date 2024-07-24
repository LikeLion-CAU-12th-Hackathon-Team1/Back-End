from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework import serializers
from .models import User

class RegisterLoginSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['name', 'email']

    def save(self, request):
        user = User.objects.create(
            name = self.validated_data['name'],
            email = self.validated_data['email']
        )

        return user
