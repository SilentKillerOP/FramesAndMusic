import os
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
import zipfile
from django.core.files.storage import FileSystemStorage
import cv2
from moviepy.editor import VideoFileClip
import shutil


def video_to_frames(video_path):
    video = cv2.VideoCapture(video_path)
    print("Opened" if video.isOpened() else "Not Found")

    fps = video.get(cv2.CAP_PROP_FPS)
    video_name = os.path.splitext(os.path.basename(video_path))[
        0
    ]  # Extract video file name without extension
    os.makedirs(os.path.join(settings.MEDIA_ROOT, "frames", video_name), exist_ok=True)
    frames_path = os.path.join(settings.MEDIA_ROOT, "frames", video_name)  # Get the directory of the video
    audio_path = os.path.join(frames_path, f"{video_name}.mp3")  
    # # Path to save the extracted audio

    interval = int(fps)  # Interval to save frames (1 frame per second)
    current_frame = 0
    saved_frames = 0

    while True:
        ret, frame = video.read()
        if not ret:
            break

        current_frame += 1
        if current_frame % interval == 0:
            frame_path = os.path.join(
                frames_path, f"{video_name}_{saved_frames+1}.png"
            )  # Path to save the frame image
            cv2.imwrite(frame_path, frame)
            saved_frames += 1

    video.release()
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path)
    video_clip.close()
    return frames_path

def create_zip(directory_path, zip_file_path):
    shutil.make_archive(zip_file_path, 'zip', directory_path)

def video_upload(request):
    if request.method == "POST" and request.FILES.get("video"):
        # Handle the uploaded video file
        video_file = request.FILES["video"]
        # Create a unique filename for storing the video

        video_directory = os.path.join(settings.MEDIA_ROOT, "videos")
        fs = FileSystemStorage(location=video_directory)
        filename = fs.save(video_file.name, video_file)
        zip_dir = video_to_frames(os.path.join(video_directory, filename))
        zip_filename = f"{os.path.splitext(filename)[0]}"
        zip_file_path = os.path.join(settings.MEDIA_ROOT, zip_filename)
        create_zip(zip_dir, zip_file_path)
        shutil.rmtree(zip_dir)
        zip_file_path = f"{zip_file_path}.zip"

        with open(zip_file_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/zip")
            response["Content-Disposition"] = f'attachment; filename="{zip_filename}.zip"'

        # Delete the temporary zip file from the server
        os.remove(zip_file_path)
        os.remove(os.path.join(video_directory, filename))

        return response

    return render(request, "upload.html")
