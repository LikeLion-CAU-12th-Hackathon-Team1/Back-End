from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

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
    