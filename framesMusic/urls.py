from django.urls import path
from . import views

urlpatterns = [
    path('', views.video_upload, name='video_upload'),
]
