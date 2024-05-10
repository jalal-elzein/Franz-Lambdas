import json
import pickle
import os

import boto3
import note_seq
from music21 import converter, metadata, environment

from midi_program_mapping import get_midi_program_mapping

INPUT_BUCKET_NAME = os.environ.get("INPUT_BUCKET_NAME", "audio-transcribed-1")
LOCAL_INPUT_DIRECTORY = os.environ.get("LOCAL_INPUT_DIRECTORY", "input")
LOCAL_OUTPUT_DIRECTORY = os.environ.get("LOCAL_OUTPUT_DIRECTORY", "output")
TARGET_BUCKET_NAME = os.environ.get("TARGET_BUCKET_NAME", "audio-transcribed-1")
NS_FILENAME = os.environ.get("NS_FILENAME", "note_sequence.pkl")
MIDI_FILENAME = os.environ.get("MIDI_FILENAME", "result.mid")
PDF_FILENAME = os.environ.get("PDF_FILENAME", "result.pdf")
PROGRAM_MAPPING = get_midi_program_mapping()

us = environment.UserSettings()
us['musescoreDirectPNGPath'] = '/usr/bin/mscore'
us['directoryScratch'] = '/tmp'


def get_program_by_name(name):
    mapping = PROGRAM_MAPPING
    for i, item in enumerate(mapping):
        if item["instrument"] == name:
            return i
    return -1


def download_audio_file(bucket_name, key, local_dir, new_filename):
    s3 = boto3.client("s3")
    local_file_path = os.path.join(local_dir, new_filename)
    try:
        s3.download_file(bucket_name, key, local_file_path)
        print(f">> Downloaded {bucket_name}/{key} --> {local_file_path}")
    except Exception as e:
        print(f">> Error downloading audio file from S3: {e}")
        raise e
    

def generate_outputs(note_seq_x, output_dir, title=""):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # NoteSequence -> MIDI
    note_seq.sequence_proto_to_midi_file(
        note_seq_x, 
        os.path.join(output_dir, MIDI_FILENAME)
    )
    # NoteSequence -> Pickle
    with open(os.path.join(output_dir, NS_FILENAME), 'wb') as f:
        pickle.dump(note_seq_x, f)
    # MIDI -> MIDI Stream
    midi_stream = converter.parse(os.path.join(output_dir, MIDI_FILENAME))
    # Edit Stream Metadata
    if len(midi_stream.parts) == 1:
        midi_stream.parts[0].partName = PROGRAM_MAPPING[
            note_seq_x.notes[0].program
        ]["instrument"]
    metadata_x = metadata.Metadata()
    metadata_x.title = title
    print(metadata_x.title)
    midi_stream.getInstruments().show("text")
    # MIDI Stream -> PDF & MusicXML
    midi_stream.write(
        "musicxml.pdf",
        os.path.join(output_dir, PDF_FILENAME),
        makeNotation=True,
        metadata=metadata_x,
        MetaSpec_instrument_name=True,
    )

# bucket_name/username/song::timestamp/Custom/*.*
def upload_folder_to_s3(local_folder_path, bucket_name, username, song_title, ):
    s3 = boto3.client("s3")
    key = f"{username}/{song_title}/Custom/"
    for root, dirs, files in os.walk(local_folder_path):
        for xfile in files:
            local_file_path = os.path.join(root, xfile)
            s3_file_path = os.path.join(key, xfile)
            s3.upload_file(local_file_path, bucket_name, s3_file_path)
            print(f">> Uploaded {os.path.join(root, xfile)} --> {os.path.join(bucket_name, key, xfile)}")


def lambda_handler(event, context):
    # take as input the user, song-title, from instruments, and to instrument
    body = event.get('body')
    if body:
        data = json.loads(body)
        username = data['username']  # username
        song_title = data['song_title']  # song::timestamp
        from_instruments = data['from_inst']  # [inst_name, inst_name]
        to_instrument = data['to_inst'] # inst_name

        if not os.path.exists(LOCAL_OUTPUT_DIRECTORY):
            os.makedirs(LOCAL_OUTPUT_DIRECTORY)

        # construct the path to the audio file
        if not os.path.exists(LOCAL_INPUT_DIRECTORY):
            os.makedirs(LOCAL_INPUT_DIRECTORY)
        
        # download the note_sequences
        for instrument in from_instruments:
            key = f"{username}/{song_title}/{instrument}/{NS_FILENAME}"
            filename = f"{instrument}.pkl"
            download_audio_file(INPUT_BUCKET_NAME, key, LOCAL_INPUT_DIRECTORY, filename)
        download_audio_file(
            INPUT_BUCKET_NAME,
            f"{username}/{song_title}/{to_instrument}/{NS_FILENAME}",
            LOCAL_INPUT_DIRECTORY,
            f"original.pkl"
        )
        
        # load the note_sequences for each of the instruments
        note_sequences = []
        for filename in os.listdir(LOCAL_INPUT_DIRECTORY):
            if filename.endswith('.pkl'):
                file_path = os.path.join(LOCAL_INPUT_DIRECTORY, filename)
                with open(file_path, 'rb') as f:
                    try:
                        temp_ns = pickle.load(f)
                        note_sequences.append(temp_ns)
                    except pickle.UnpicklingError:
                        print(f"Error unpickling file: {file_path}")
        
        # loop through the "from instruments" to override their program
        new_program = get_program_by_name(to_instrument)
        for ns in note_sequences:
            for note in ns.notes:
                note.program = new_program
        
        # combine the instruments into a new notesequence
        new_ns = note_seq.NoteSequence()
        for ns in note_sequences:
            for note in ns.notes:
                new_ns.notes.append(note)
        
        # generate output of the note_sequence
        generate_outputs(new_ns, LOCAL_OUTPUT_DIRECTORY)
        
        # upload output to S3
        upload_folder_to_s3(
            LOCAL_OUTPUT_DIRECTORY, 
            TARGET_BUCKET_NAME, 
            username, 
            song_title
        )
        
        return {
            "statusCode": 200,
            "body": "Success"
        }
    else:
        return {
            "statusCode": 500,
            "body": "Body does not exist"
        }