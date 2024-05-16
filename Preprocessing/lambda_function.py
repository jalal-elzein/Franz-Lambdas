import os
from urllib.parse import unquote_plus
from pydub import AudioSegment

from pedalboard.io import AudioFile 
from pedalboard import Pedalboard, PeakFilter, NoiseGate
import boto3

INPUT_DIR = os.environ.get("INPUT_DIR", "/tmp/input")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/tmp/output")
SAMPLE_RATE = os.environ.get("SAMPLE_RATE", 16000.0)
OUTPUT_BUCKET = os.environ.get("OUTPUT_BUCKET", "audio-processed-1")



def convert_to_mp3(input_file, output_file):
    # Load the audio file
    audio = AudioSegment.from_file(input_file)

    # Export the audio to MP3 format
    audio.export(output_file, format="mp3")


def download_audio_file(bucket_name, key, audio_file_path):
    s3 = boto3.client("s3")
    try:
        s3.download_file(bucket_name, key, audio_file_path)
        print(f"{bucket_name}/{key} has been downloaded to {audio_file_path}")
    except Exception as e:
        print(f">> Error downloading audio file from S3: {e}")
        raise e
    

def upload_audio_file(local_filepath, bucket_name, key):
    s3 = boto3.client("s3")
    try:
        s3.upload_file(local_filepath, bucket_name, key)
        print(f"{local_filepath} has been uploaded to {bucket_name}/{key}")
    except Exception as e:
        print(f">> Error uploading audio file to S3: {e}")
        raise e

def display_contents(directory):
    print(os.getcwd())
    print(os.listdir())
    for root, _, files in os.walk(directory):
        for file in files:
            print(os.path.join(root, file))


def lambda_handler(event, context):
    # parse information from trigger event
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]  # 'audio-unprocessed-1'
    key = unquote_plus(event["Records"][0]["s3"]["object"]["key"])  # 'username/song::timestamp/file.mp3'
    filename = os.path.basename(key) # 'file.mp3'
    prefix = os.path.dirname(key) # 'username/song::timestamp/'

    # create necessary directories if they don't exist 
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # download audio from unprocessed audio bucket
    print(f">> Downloading audio...")
    input_audio_filename = os.path.join(INPUT_DIR, filename) # 'tmp/input/file.mp3'
    download_audio_file(
        bucket_name,
        key,
        input_audio_filename
    )


    convert_to_mp3(os.path.join(INPUT_DIR, filename), os.path.join(INPUT_DIR, "ouput.mp3"))
    input_audio_filename = os.path.join(INPUT_DIR, "output.mp3")
    
    display_contents
    # load audio 
    print(">> Loading audio file...")
    with AudioFile(input_audio_filename).resampled_to(SAMPLE_RATE) as f:
        audio = f.read(f.frames)

    # define the effects
    board = Pedalboard([
        PeakFilter(),
        NoiseGate()
    ])

    # run the processing
    print(">> Processing...")
    effected = board(audio, SAMPLE_RATE)

    # write out the processed audio 
    print(">> Writing final output...")
    output_audio_filename = os.path.join(OUTPUT_DIR, filename) # 'tmp/output/file.mp3'
    with AudioFile(output_audio_filename, 'w', SAMPLE_RATE, effected.shape[0]) as f:
        f.write(effected)
    
    # upload output to processed bucket
    print(">> Uploading audio...")
    upload_audio_file(
        output_audio_filename, 
        OUTPUT_BUCKET,
        os.path.join(prefix, filename)
    )
