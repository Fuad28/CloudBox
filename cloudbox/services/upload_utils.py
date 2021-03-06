import io
import os
import base64
from datetime import datetime
from PIL import Image

from mongoengine import connect, disconnect
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


def resize_picture(media):
    """reduce profile picture sizes"""
    output_size = (512, 512)
    return Image.open(media).resize(output_size)


def rename_file(filename: str):
    """
    Rename a file using its original name (modified) and current timestamp
    """
    uploaded_date = datetime.utcnow()

    if filename is None:
        raise ValueError("Filename is required")

    splitted = filename.rsplit(".", 1)
    if len(splitted) < 2:
        raise ValueError("Filename must have an extension")

    updated_filename = splitted[0]
    file_extension = splitted[1]

    # Make sure that filename is secure
    updated_filename = secure_filename(updated_filename.lower())

    # Combining filename and timestamp
    updated_filename = f"{uploaded_date.strftime('%Y%m%d%H%M%S')}--{updated_filename}"

    # Combining the updated filename and file extension
    updated_filename = f"{updated_filename}.{file_extension}"

    return updated_filename


def process_file_to_stream(file: FileStorage, to_utf8: bool = False) -> dict:
    """
    Notice that since celery serializer (json) can't take bytes datatype,
    so, we need to convert it from base64 bytes to utf-8 format.
    But we don't need to do that when using threading
    """
    stream = base64.b64encode(file.stream.read())
    result = {
        "stream": stream if not to_utf8 else stream.decode("utf-8"),
        "name": file.name,
        "filename": rename_file(file.filename),
        "content_type": file.content_type,
        "content_length": file.content_length,
        "headers": {header[0]: header[1] for header in file.headers},
    }

    return result

def process_stream_to_file(data: dict) -> str:
    """
    Convert data back from base64 encoded bytes/utf-8 to file
    """
    data["stream"] = base64.b64decode(data["stream"])
    data["stream"] = io.BytesIO(data["stream"])
    file= FileStorage(**data)
    
    return file, data["content_type"]

#configure boto3
# s3 = boto3.client(
#   "s3", 
#   aws_access_key_id= os.environ.get("AWS_ACCESS_KEY_ID"), 
#   aws_secret_access_key= os.environ.get("AWS_SECRET_ACCESS_KEY"),
#   )
s3= ""

def upload_file(file: FileStorage) -> str:
    """
    Upload file using normal synchronous way
    """
    s3.upload_fileobj(
        file,
        os.getenv('S3_BUCKET_NAME'),
        file.filename,
        ExtraArgs={
            "ContentType": file.content_type,
        },
    )
    return f"{os.getenv('S3_BUCKET_BASE_URL')}/{file.filename}"


def upload_file_from_stream(data: dict) -> str:
    """
    Upload file to S3 by first converting back from base64 encoded bytes/utf-8 to file
    """
    data["stream"] = base64.b64decode(data["stream"])
    data["stream"] = io.BytesIO(data["stream"])
    file = FileStorage(**data)

    s3.upload_fileobj(
        file,
        os.getenv('S3_BUCKET_NAME'),
        file.filename,
        ExtraArgs={
            "ContentType": file.content_type,
        },
    )
    return f"{os.getenv('S3_BUCKET_BASE_URL')}/{file.filename}"


def mongo_connect():
    """
    We are supposed to connect to the  database inside the task.
    The reason is because child processes (created by Celery) must have their own instance of mongo client.
    re: https://stackoverflow.com/questions/49743258/mongodb-into-a-celery-task-flask-application

    """
    disconnect(alias='default')
    return connect("cloudbox")
