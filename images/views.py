from django.shortcuts import render

# Create your views here.

# views.py 파일에 작성
from django.shortcuts import render
from django.http import JsonResponse
from .utils import *
import os

def upload_images_from_folder_view(request):
    if request.method == 'POST':
        folder_path = request.POST.get('folder_path')
        if folder_path:
            for filename in os.listdir(folder_path):
                if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
                    image_path = os.path.join(folder_path, filename)
                    place_code = int(os.path.splitext(filename)[0])  # 파일 이름이 place_code라고 가정
                    image_url = upload_and_resize_image(image_path, place_code)
                    if image_url:
                        save_image_url_to_place(place_code, image_url)
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Folder path not provided'})
    return render(request, 'upload_images_from_folder.html')
