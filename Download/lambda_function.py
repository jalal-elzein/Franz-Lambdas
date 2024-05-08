from __future__ import unicode_literals
import json
import os
import subprocess
import boto3
import youtube_dl
from time import time


LOCAL_OUTPUT_FOLDER= "/tmp/outputs"
YTDL_OPTIONS = {
    "noplaylist": "",
    "format": "bestaudio[filesize<10M]",
    "outtmpl": f"{LOCAL_OUTPUT_FOLDER}/%(title)s-%(channel)s.%(ext)s",
    "cachedir" : "/tmp/youtube-dl-cache"
}
target_file_type = "m4a"
output_bucket_name = "audio-unprocessed-1"


def lambda_handler(event, context):
    try:
        timestamp = int(time())
        print(f">> Request UNIX timestamp: {timestamp}")
        if not os.path.exists(LOCAL_OUTPUT_FOLDER):
            os.makedirs(LOCAL_OUTPUT_FOLDER)
            print(">> Created local output directory")
        request_body = event
        youtube_link = request_body['queryStringParameters']['url']
        username = request_body['queryStringParameters']['username']
        song_title = request_body['queryStringParameters']['song_title']
        print(f"youtube_link: {youtube_link}")
        print(f"username: {username}")
        print(f"song_title: {song_title}")
        # download
        print(">> Downloading audio...")
        download_response = download_audio(youtube_link)
        print(download_response)
        print(f">> Forcing type: {target_file_type}")
        force_type(LOCAL_OUTPUT_FOLDER, target_file_type)
        # put on s3
        # {bucket_name}/{username}/{song_title}-{timestamp}/{file_name}
        print(">> Uploading outputs to S3")
        upload_response = upload_audio(
            bucket_name=output_bucket_name, 
            prefix=f"{username}/{song_title}-{timestamp}", 
            local_directory=LOCAL_OUTPUT_FOLDER,
            xtype=target_file_type
        )
        return {
            'statusCode': 200,
            'body': json.dumps(upload_response),
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps(str(e))
        }


def get_filenames(directory):
    filenames = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            filenames.append(filename)
    return filenames


def download_audio(url: str):
    try:
        with youtube_dl.YoutubeDL(YTDL_OPTIONS) as ydl:
                    ydl.download([url])
        return f">> Download successfull"
    except Exception as e:
        return f">> Error downloading video: {e}"


def upload_audio(bucket_name, prefix, local_directory, xtype):
    s3_client = boto3.client('s3')
    filenames = get_filenames(local_directory)
    for filename in filenames:
        if filename.endswith(f'.{xtype}'):
            file_path = os.path.join(local_directory, filename)
            try:
                s3_key = f"{prefix}/{filename}"
                response = s3_client.upload_file(file_path, bucket_name, s3_key)
                print(f"Uploaded {filename} to S3 bucket {bucket_name} with prefix {prefix}")
                print(f"s3://{bucket_name}/{prefix}/{filename}")
                print()
                return {
                    "s3_key": s3_key,
                    "bucket_name": bucket_name,
                    "response": response
                }
            except Exception as e:
                print(f"Error uploading {filename}: {e}")


def force_type(source_folder, xtype):
    for filename in os.listdir(source_folder):
        file_path = os.path.join(source_folder, filename)
        if os.path.isfile(file_path) and not filename.endswith(f'.{xtype}'):
            output_file = os.path.splitext(filename)[0] + '.m4a'
            output_path = os.path.join(source_folder, output_file)
            try:
                subprocess.run(['ffmpeg', '-i', file_path, '-c:a', 'aac', '-b:a', '128k', output_path], check=True)
                print(f"Converted {filename} to {output_file}")
                os.remove(file_path)
                print(f"Deleted {filename}")
            except subprocess.CalledProcessError as e:
                print(f"Error converting {filename}: {e}")
