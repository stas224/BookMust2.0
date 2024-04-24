import boto3


def get_s3():
    return boto3.client(
        's3',
        endpoint_url='http://localhost:4566',
        aws_access_key_id='',
        aws_secret_access_key='',
        region_name=''
    )
