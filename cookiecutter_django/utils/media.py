import os
import shutil
import subprocess
from datetime import timedelta
from io import BytesIO
from time import time

from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.timezone import now
from PIL import Image

from core.utils.custom_exceptions import CustomError
from core.utils.validators import (
    _VALID_AUDIO_EXTENSIONS,
    _VALID_IMAGE_EXTENSIONS,
    _VALID_VIDEO_EXTENSIONS,
)

logger = get_task_logger(__name__)


APPS_DIR = settings.APPS_DIR


class MediaHelper:
    """
    Utility class to manage media files
    """

    @staticmethod
    def _upload_path_with_folder(model, filetype, filename):
        """
        function to generate upload path for media files to prevent duplicate
        """
        path = f"{filetype}/{model}/{timezone.localdate()}"
        ext = filename.rsplit(".", 1)
        filename = slugify(f"{int(time())}-{ext[0]}")

        if len(ext) > 1:
            filename += "." + ext[-1]

        return f"{path}/{filename.split('.', 1)[0]}/{filename}"

    @staticmethod
    def _upload_path_file_only(model, filetype, filename):
        """
        function to generate upload path for media files to prevent duplicate
        """
        path = f"{filetype}/{model}/{timezone.localdate()}"
        ext = filename.rsplit(".", 1)
        filename = slugify(f"{int(time())}-{ext[0]}")

        if len(ext) > 1:
            filename += "." + ext[-1]

        return f"{path}/{filename}"

    @staticmethod
    def get_image_upload_path(model, filename):
        """generate upload path for images to prevent duplicate"""
        return MediaHelper._upload_path_file_only("files", "images", filename)

    @staticmethod
    def get_video_upload_path(model, filename):
        """generate upload path for videos to prevent duplicate"""
        return MediaHelper._upload_path_with_folder("files", "videos", filename)

    @staticmethod
    def get_audio_upload_path(model, filename):
        """generate audio path for audio to prevent duplicate"""
        return MediaHelper._upload_path_with_folder("files", "audios", filename)

    @staticmethod
    def get_document_upload_path(model, filename):
        """generate media path for all medias to prevent duplicate"""
        ext = filename.rsplit(".", 1)
        return MediaHelper._upload_path_file_only(
            model, f"{ext}/{now().date()}", filename
        )

    @staticmethod
    def upload_path_finder(model, filename):
        """Route the file to the appropriate formatter"""
        ext = str(filename.rsplit(".", 1)[-1]).lower()
        ext = "." + ext
        if ext in _VALID_IMAGE_EXTENSIONS:
            return MediaHelper.get_image_upload_path(model, filename)
        elif ext in _VALID_VIDEO_EXTENSIONS:
            return MediaHelper.get_video_upload_path(model, filename)
        elif ext in _VALID_AUDIO_EXTENSIONS:
            return MediaHelper.get_audio_upload_path(model, filename)
        else:
            return MediaHelper.get_document_upload_path(model, filename)

    def get_video_duration(video_path):
        """
        Get the duration of a video file.

        Args:
            video_path (str): The path to the video file.

        Returns:
            float or None: The duration of the video in seconds, or None if an error occurred.
        #"""
        command = [
            "ffprobe",
            "-i",
            video_path,
            "-show_entries",
            "format=duration",
            "-v",
            "quiet",
            "-of",
            "csv=p=0",
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            duration = timedelta(seconds=float(result.stdout.strip())).total_seconds()
        if video_path:
            return duration
        else:
            raise CustomError.BadRequest(
                detail="Could not determine the duration of the video."
            )

    @staticmethod
    def generate_image_file(name, ext="png", size=(50, 50), color=(256, 0, 0)) -> File:
        """For testing purpose"""
        file_obj = BytesIO()
        image = Image.new("RGBA", size=size, color=color)
        image.save(file_obj, ext)
        file_obj.seek(0)
        return File(file_obj, name=name)

    @staticmethod
    def convert_to_wav(media_path: str):
        path = media_path.rsplit(".", 1)[0]
        output = f"{path}.wav"
        name = output.rsplit("/", 1)[1]
        cmd = [
            "ffmpeg",
            "-i",
            media_path,
            "-ar",
            "16000",  # Sample rate: 16 kHz
            "-ac",
            "1",  # Mono audio
            "-sample_fmt",
            "s16",  # 16-bit PCM
            "-f",
            "wav",
            output,
        ]
        result = subprocess.run(cmd, check=True)
        if result.returncode == 0:
            return output, name


class FolderDeletionHandler(FileSystemStorage):
    def delete(self, name: str) -> None:
        try:
            if os.path.isdir(name):
                shutil.rmtree(name)
        except FileNotFoundError:
            pass
        return super().delete(name)


folder_deletion_handler = FolderDeletionHandler()


class CustomTemporaryFolder:
    def __init__(self, folder_name):
        self.folder_path = str(APPS_DIR / "media")
        self.folder_name = folder_name

    def __enter__(self):
        self.temp_folder = f"{self.folder_path}/{self.folder_name}"
        os.makedirs(self.temp_folder, exist_ok=True)
        return self.temp_folder

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
