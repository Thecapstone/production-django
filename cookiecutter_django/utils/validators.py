import os

from core.utils.custom_exceptions import CustomError

_VALID_FILE_EXTENSIONS = [
    ".doc",
    ".docx",
    ".jpg",
    ".pdf",
    ".png",
    ".pptx",
    ".xls",
    ".xlsx",
]

_VALID_AUDIO_EXTENSIONS = [
    ".mp3",
    ".aac",
    ".wav",
    ".m4a",
]

_VALID_VIDEO_EXTENSIONS = [
    "hls",
    ".avi",
    ".flv",
    ".mkv",
    ".mov",
    ".mp4",
    ".webm",
    ".wmv",
    ".m4a",
    ".mp3",
]

_VALID_IMAGE_EXTENSIONS = [
    ".jfif",
    ".jpeg",
    ".jpg",
    ".png",
]

_VALID_DOCS_EXTENSIONS = [
    ".yaml",
    ".yml",
    ".json",
]

_ALL_VALID_EXTENSIONS = (
    _VALID_FILE_EXTENSIONS
    + _VALID_VIDEO_EXTENSIONS
    + _VALID_AUDIO_EXTENSIONS
    + _VALID_IMAGE_EXTENSIONS
)


class FileValidatorHelper:
    """
    Helper class to validate files
    """

    @staticmethod
    def validate_file_extension(obj):
        """
        Checks that we are using a valid file extension
        """

        ext = os.path.splitext(obj.name)[1]

        if ext.lower() not in _VALID_FILE_EXTENSIONS:
            raise CustomError.BadRequest(
                "Only pdf, doc, docx, xlsx, xls, jpg, pptx "
                + "and png file is supported."
            )

    @staticmethod
    def validate_doc_extension(obj):
        """
        Checks that we are using a valid file extension
        """

        ext = os.path.splitext(obj.name)[1]

        if ext.lower() not in _VALID_DOCS_EXTENSIONS:
            raise CustomError.BadRequest("Only yaml, yml, json file is supported.")

    @staticmethod
    def validate_multiple_filetype_extension(obj):
        """
        Checks that we are using a valid file extension
        """

        ext = os.path.splitext(obj.name)[1]

        if ext.lower() not in _ALL_VALID_EXTENSIONS:
            raise CustomError.BadRequest(
                f"Only {_ALL_VALID_EXTENSIONS} files are supported."
            )

    @staticmethod
    def validate_audio_extension(obj):
        """
        Checks that we are using a valid audio extension
        """

        ext = os.path.splitext(obj.name)[1]

        if ext.lower() not in _VALID_AUDIO_EXTENSIONS:
            raise CustomError.BadRequest("Only mp3, aac, wav files are supported.")

    @staticmethod
    def validate_file_size(obj):
        """
        Checks that file size is not too large
        """
        filesize = obj.size

        if filesize > 10_000_000:
            mb = 10_000_000 / 1048576  # Convert the file size from bytes to MB
            raise CustomError.BadRequest(
                f"The maximum file size that can be uploaded is {mb}MB"
            )

        return obj

    @staticmethod
    def validate_image_size(obj):
        """
        Checks that logo size is not too large
        """
        filesize = obj.size
        if filesize > 2_097_152:
            raise CustomError.BadRequest(
                "The maximum file size that can be uploaded is 2MB"
            )

        return obj

    @staticmethod
    def validate_image_extension(obj):
        ext = os.path.splitext(obj.name)[1]

        if ext.lower() not in _VALID_IMAGE_EXTENSIONS:
            raise CustomError.BadRequest("only jpg, jpeg, jfif and png file supported.")
