import os
from io import BytesIO

import boto3

bucket_name = "bookmust"


def get_s3():
    return boto3.client(
        's3',
        endpoint_url='http://localhost:4566',
        aws_access_key_id='12',
        aws_secret_access_key='12',
        region_name='us-east-1'
    )


def get_presigned_url(key):
    return get_s3().generate_presigned_url(
        'get_object',
        Params={
            "Bucket": bucket_name,
            "Key": key
        }
    )


def fill_s3_if_not_filled():
    buckets = [b["Name"] for b in get_s3().list_buckets()["Buckets"]]
    if bucket_name in buckets:
        return

    get_s3().create_bucket(Bucket=bucket_name)

    media_dir = os.path.join(os.getcwd(), "media")

    flags_dir = os.path.join(media_dir, "flags")
    for flag in os.listdir(flags_dir):
        s3 = get_s3()
        flag_path = os.path.join(flags_dir, flag)
        s3.upload_file(flag_path, bucket_name, f"flags/{flag}")
    print("flags ok")

    covers_dir = os.path.join(media_dir, "covers")
    for cover in os.listdir(covers_dir):
        s3 = get_s3()
        cover_path = os.path.join(covers_dir, cover)
        s3.upload_file(cover_path, bucket_name, f"covers/{cover}")
        with BytesIO(b"file content") as b:
            s3.upload_fileobj(b, bucket_name, f"books/{cover.replace('.png', '.txt')}")
    print("covers and books ok")

    icons_dir = os.path.join(media_dir, "icons")
    for icon in os.listdir(icons_dir):
        s3 = get_s3()
        icon_path = os.path.join(icons_dir, icon)
        s3.upload_file(icon_path, bucket_name, f"icons/{icon}")
    print("icons ok")
