import os
import boto3

def download_audio_file(bucket_name, key, audio_file_path):
    s3 = boto3.client("s3")
    try:
        s3.download_file(bucket_name, key, audio_file_path)
    except Exception as e:
        print(f">> Error downloading audio file from S3: {e}")
        raise e
    
def upload_folder_to_s3(local_folder_path, bucket_name, s3_prefix=""):
    # Initialize S3 client
    s3 = boto3.client("s3")
    for root, dirs, files in os.walk(local_folder_path):
        for filename in files:
            local_file_path = os.path.join(root, filename)
            s3_key = os.path.join(
                s3_prefix, os.path.relpath(local_file_path, local_folder_path)
            )
            s3.upload_file(local_file_path, bucket_name, s3_key)
            print(f"Uploaded {local_file_path} to S3 as {bucket_name}/{s3_key}")

def write_to_dynamo(table_name, item):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    try:
        response = table.put_item(Item=item)
        print(f"Item written to {table_name} table:")
        print(item)
        return response
    except Exception as e:
        print(f"Error writing item to {table_name} table:")
        print(e)
        raise e
    