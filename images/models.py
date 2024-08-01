# from django.db import models

# # Create your models here.

# from PIL import Image
# import io
# import boto3
# from botocore.exceptions import NoCredentialsError
# import mysql.connector
# from mysql.connector import Error
# from config.settings import AWS_STORAGE_BUCKET_NAME, AWS_S3_CUSTOM_DOMAIN, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

# # image_path = ""

# # with open(image_path, "rb") as image_file:
# #     img = Image.open(image_file)

# # s3 = boto3.client('s3',
# #                   aws_access_key_id = AWS_ACCESS_KEY_ID,
# #                   aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
# #                   region_name = AWS_REGION)

# # bucket_name = AWS_STORAGE_BUCKET_NAME
# # s3_file_name = AWS_S3_CUSTOM_DOMAIN

# # try:
# #     img_byte_arr = io.ByteIO()
# #     img.save(img_byte_arr, format='PNG')
# #     img_byte_arr.seek(0)
# #     s3.upload_fileobj(img_byte_arr, bucket_name, s3_file_name)
# #     print("Upload Successful")
# # except FileNotFoundError:
# #     print("The file was not found")
# # except NoCredentialsError:
# #     print("Credentials not available")

# # # S3 URL 생성
# # region = 'YOUR_REGION'
# # s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_file_name}"


# # connection = mysql.connector.connect(
# #     host='YOUR_HOST',
# #     database='YOUR_DATABASE',
# #     user='YOUR_USERNAME',
# #     password='YOUR_PASSWORD'
# # )

# # if connection.is_connected():
# #     cursor = connection.cursor()
# #     # 테이블 생성 (이미 존재하는 경우 생략 가능)
# #     cursor.execute('''
# #         CREATE TABLE IF NOT EXISTS images (
# #             id INT AUTO_INCREMENT PRIMARY KEY,
# #             url VARCHAR(255) NOT NULL
# #         )
# #     ''')
# #     # URL 삽입
# #     insert_query = "INSERT INTO images (url) VALUES (%s)"
# #     cursor.execute(insert_query, (s3_url,))
# #     connection.commit()

# #     # 데이터베이스 연결 종료
# #     cursor.close()
# #     connection.close()
# #     print("MySQL connection is closed")
# # else:
# #     print("Failed to connect to MySQL")


# def upload_and_resize_image(image_path, place_code, bucket_name='your-bucket-name', region='your-region', max_size=(292, 260)): # width, height = 292, 260
#     # 이미지 파일 로드 및 크기 조정
#     img = Image.open(image_path)
#     img.thumbnail(max_size, Image.ANTIALIAS)
    
#     # 이미지 파일을 메모리에 저장
#     img_byte_arr = io.BytesIO()
#     img.save(img_byte_arr, format='PNG')
#     img_byte_arr.seek(0)
    
#     # S3에 업로드
#     s3 = boto3.client('s3', 
#                     aws_access_key_id=AWS_ACCESS_KEY_ID, 
#                     aws_secret_access_key=AWS_SECRET_ACCESS_KEY, 
#                     region_name=AWS_REGION)
#     s3_file_name = f'{place_code}.png'
#     try:
#         s3.upload_fileobj(img_byte_arr, bucket_name, s3_file_name)
#         print("Upload Successful")
#     except Exception as e:
#         print(f"Upload failed: {e}")
#         return None

#     # S3 URL 생성
#     s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_file_name}"
#     return s3_url

# def save_image_url_to_place(place_code, image_url):
#     from .models import Place  # 모델을 로컬로 임포트
#     try:
#         place = Place.objects.get(place_code=place_code)
#         place.image = image_url
#         place.save()
#         print(f"Image URL saved to Place model for place_code {place_code}")
#     except Place.DoesNotExist:
#         print(f"No Place found with place_code {place_code}")