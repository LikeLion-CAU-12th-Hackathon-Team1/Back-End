from .models import Place
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
import boto3
from uuid import uuid4
from django.core.files.base import ContentFile
from .models import Sigg, Sido
from PIL import Image
from io import BytesIO
from config.settings import AWS_STORAGE_BUCKET_NAME, AWS_S3_CUSTOM_DOMAIN, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

class PlaceCreateSerializer(serializers.ModelSerializer):
    sigg_id = ReadOnlyField(source='sigg.sigg_id')
    placename = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    category = serializers.IntegerField(required=True)
    photo = serializers.ImageField(write_only=True)

    class Meta:
        model = Place
        fields = '__all__'

    def create(self, validated_data):
        photo = validated_data.pop('photo', None)
        photo_url = self.upload_image(photo)
        validated_data['image'] = photo_url
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            photo_url = self.upload_to_s3(photo)
            instance.image = photo_url

        instance.place_code = validated_data.get('place_code', instance.place_code)
        instance.save()
        return instance

    def upload_image(self, photo):
        s3_client = boto3.client(
            's3',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        img = Image.open(photo)
        width, height = 292, 260
        resized_img = img.resize((width, height))
        img_byte_arr = BytesIO()
        resized_img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        # BytesIO 객체를 ContentFile로 변환
        file_content = ContentFile(img_byte_arr.read())
        file_name = f'{uuid4()}.jpg'
        s3_client.upload_fileobj(
            file_content,
            AWS_STORAGE_BUCKET_NAME,
            f'media/{file_name}',
            ExtraArgs={'ContentType': 'image/jpeg'}
        )
        return f'https://{AWS_S3_CUSTOM_DOMAIN}/media/{file_name}'

class ListSidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sido
        fields = '__all__'

class ListSiggSerializer(serializers.ModelSerializer):
    sido = serializers.PrimaryKeyRelatedField(queryset=Sido.objects.all())

    class Meta:
        model = Sigg
        fields = '__all__'
