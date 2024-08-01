from PIL import Image
import os
import io
import boto3
from django.conf import settings
from config.settings import AWS_STORAGE_BUCKET_NAME, AWS_S3_CUSTOM_DOMAIN, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


# def upload_and_resize_image(image_path, place_code, bucket_name=None, region=None, max_size=(800, 800)): 
#     if bucket_name is None:
#         bucket_name = AWS_STORAGE_BUCKET_NAME
#     if region is None:
#         region = AWS_REGION

#     # 이미지 파일 로드 및 크기 조정
#     with Image.open(image_path) as image:
#         resized_image = image.resize((292, 260), Image.ANTIALIAS)

#         # 이미지 파일을 메모리에 저장
#         img_byte_arr = io.BytesIO()
#         resized_image.save(img_byte_arr, format='PNG')
#         img_byte_arr.seek(0)

#     # S3에 업로드
#     s3 = boto3.client(
#         's3', 
#         aws_access_key_id=AWS_ACCESS_KEY_ID, 
#         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#         region_name=region
#     )
#     s3_file_name = f'{place_code}.png'
#     try:
#         s3.upload_fileobj(img_byte_arr, bucket_name, s3_file_name)
#         print("Upload Successful")
#     except Exception as e:
#         print(f"Upload failed: {e}")
#         return None

#     # # S3 URL 생성
#     # if AWS_S3_CUSTOM_DOMAIN:
#     #     s3_url = f"https://{AWS_S3_CUSTOM_DOMAIN}/{s3_file_name}"
#     # else:
#     #     s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_file_name}"

#     # return s3_url

#     url = f"https://{AWS_S3_CUSTOM_DOMAIN}/{s3_file_name}"
#     return url

# def save_image_url_to_place(place_code, image_url):
#     from places.models import Place  # 모델을 로컬로 임포트
#     try:
#         place = Place.objects.get(place_code=place_code)
#         place.image = image_url
#         place.save()
#         print(f"Image URL saved to Place model for place_code {place_code}")
#     except Place.DoesNotExist:
#         print(f"No Place found with place_code {place_code}")



def upload_and_resize_image(image_path, place_code, bucket_name=None, region=None, max_size=(800, 800)):
    if bucket_name is None:
        bucket_name = AWS_STORAGE_BUCKET_NAME
    if region is None:
        region = AWS_REGION

    # 이미지 파일 로드 및 크기 조정
    with Image.open(image_path) as image:
        resized_image = image.resize((292, 260), Image.ANTIALIAS)

        # 이미지 파일을 메모리에 저장
        img_byte_arr = io.BytesIO()
        resized_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

    # S3에 업로드
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=region
    )
    s3_file_name = f'{place_code}.png'
    try:
        s3.upload_fileobj(
            img_byte_arr,
            bucket_name,
            s3_file_name,
            ExtraArgs={
                'ContentType': 'image/png'  # Content-Type을 설정하여 브라우저에서 이미지를 직접 보여줄 수 있도록 함
            }
        )
        print("Upload Successful")
    except Exception as e:
        print(f"Upload failed: {e}")
        return None

    # S3 URL 생성
    if AWS_S3_CUSTOM_DOMAIN:
        url = f"https://{AWS_S3_CUSTOM_DOMAIN}/{s3_file_name}"
    else:
        url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_file_name}"
    
    return url

def save_image_url_to_place(place_code, image_url):
    from places.models import Place  # 모델을 로컬로 임포트
    try:
        place = Place.objects.get(place_code=place_code)
        place.image = image_url
        place.save()
        print(f"Image URL saved to Place model for place_code {place_code}")
    except Place.DoesNotExist:
        print(f"No Place found with place_code {place_code}")