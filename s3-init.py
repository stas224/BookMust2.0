import os
from io import BytesIO

from bookmust.utils.s3 import get_s3

bucket_name = "bookmust"
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
