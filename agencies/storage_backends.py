# agencies/storage_backends.py

from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    """
    Custom storage class for handling media files using Amazon S3.

    Attributes:
        location (str): The location in the S3 bucket where media files will be stored.
        file_overwrite (bool): Determines whether to overwrite files with the same name.
    """
    location = 'media'
    file_overwrite = False