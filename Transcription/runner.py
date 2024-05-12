import os
from urllib.parse import unquote_plus
import time
import datetime
import pickle

import librosa
import note_seq
from music21 import converter, metadata, environment
import nest_asyncio
import pandas as pd

from model import InferenceModel
from aws_helpers import download_audio_file, upload_folder_to_s3, write_to_dynamo
from midi_program_mapping import get_midi_program_mapping

nest_asyncio.apply()

OUTPUT_BUCKET_NAME = os.environ.get("OUTPUT_BUCKET_NAME", "audio-transcribed-1")
INPUT_LOCAL_DIR_NAME = os.environ.get("INPUT_LOCAL_DIR_NAME", "input")
MODEL_CHECKPOINT_PATH = os.environ.get("MODEL_CHECKPOINT_PATH", "checkpoints/mt3/")
MODEL_NAME = os.environ.get("MODEL_NAME", "mt3")
GENERATED_OUTPUTS_LOCAL_DIR = os.environ.get("GENERATED_OUTPUTS_LOCAL_DIR", "output")
DELIMITER = os.environ.get("DELIMITER", "::")
DYNAMO_TABLE_NAME = os.environ.get("DYNAMO_TABLE_NAME", "Transcriptions")
NS_FILENAME = os.environ.get("NS_FILENAME", "note_sequence.pkl")
MIDI_FILENAME = os.environ.get("MIDI_FILENAME", "result.mid")
PDF_FILENAME = os.environ.get("PDF_FILENAME", "result.pdf")

MIDI_PROGRAM_MAPPING = get_midi_program_mapping()

us = environment.UserSettings()
us['musescoreDirectPNGPath'] = '/usr/bin/mscore'
us['directoryScratch'] = '/tmp'

os.environ["QT_QPA_PLATFORM"] = "offscreen"


def get_program_grouping(est_notes):
    n_program_ns = {}
    for note in est_notes.notes:
        if note.program not in n_program_ns:
            n_program_ns[note.program] = []
        n_program_ns[note.program].append(note)
    return n_program_ns


def print_program_ns(program_ns_x):
    mapping = MIDI_PROGRAM_MAPPING
    for num, program in enumerate(program_ns_x):
        print(
            f"Intrusment #{num} | Program #{program} | {len(program_ns_x[program])} notes | {mapping[program]}"
        )


def get_class_grouping(program_ns):
    mapping = MIDI_PROGRAM_MAPPING
    notes_per_class = {}
    for instrument in program_ns:
        # print(mapping[instrument]["class"], len(program_ns[instrument]))
        if mapping[instrument]["class"] not in notes_per_class:
            notes_per_class[mapping[instrument]["class"]] = 0
        notes_per_class[mapping[instrument]["class"]] += len(program_ns[instrument])
    return notes_per_class


def fuse_instruments(est_ns):
    mapping = MIDI_PROGRAM_MAPPING
    df = pd.DataFrame(columns=["instrument", "class", "count"])
    program_ns = get_program_grouping(est_ns)
    old_note_total = len(est_ns.notes)
    for instrument in program_ns:
        df.loc[len(df)] = [
            instrument,
            mapping[instrument]["class"],
            len(program_ns[instrument]),
        ]
    df_grouped = df.groupby("class").apply(lambda x: x.loc[x["count"].idxmax()])
    for note in est_ns.notes:
        if note.program not in df_grouped.instrument.values:
            # get its class
            classx = mapping[note.program]["class"]
            # get the instrument with the highest note count from that class
            new_inst = df_grouped.instrument[classx]
            # override the note's program
            note.program = new_inst
    new_program_ns = get_program_grouping(est_ns)
    print("-------------- fusing -----------------")
    print_program_ns(program_ns)
    print("================")
    print_program_ns(new_program_ns)
    print("================")
    print(
        f"got rid of {len(program_ns.keys()) - len(new_program_ns.keys())} instruments"
    )
    print(f"preserved total # of notes ({old_note_total}, {len(est_ns.notes)})")
    return est_ns


def discard_classes(noteseq):
    new_ns = note_seq.NoteSequence()
    mapping = MIDI_PROGRAM_MAPPING
    old_note_total = len(noteseq.notes)
    old_program_grouping = get_program_grouping(noteseq)
    notes_per_class = get_class_grouping(old_program_grouping)
    classes_to_remove = []
    for classx, num in notes_per_class.items():
        if num < (0.05 * len(noteseq.notes)):  # noteseq here was est_ns
            classes_to_remove.append(classx)
    for note in noteseq.notes:
        if mapping[note.program]["class"] not in classes_to_remove:
            new_ns.notes.append(note)
    print("-------------- discarding -----------------")
    print(f"got rid of {old_note_total - len(new_ns.notes)} notes")
    print("=====================")
    print_program_ns(old_program_grouping)
    print()
    print_program_ns(get_program_grouping(new_ns))
    print()
    print(f"# of notes ({old_note_total}, {len(new_ns.notes)})")
    return new_ns


def note_seq_to_pdf(note_seq_x, output_dir, title=""):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # NoteSequence -> MIDI
    note_seq.sequence_proto_to_midi_file(
        note_seq_x, os.path.join(output_dir, MIDI_FILENAME)
    )
    # NoteSequence -> Pickle
    with open(os.path.join(output_dir, NS_FILENAME), 'wb') as f:
        pickle.dump(note_seq_x, f)
    # MIDI -> MIDI Stream
    midi_stream = converter.parse(os.path.join(output_dir, MIDI_FILENAME))
    # Edit Stream Metadata
    if len(midi_stream.parts) == 1:
        midi_stream.parts[0].partName = MIDI_PROGRAM_MAPPING[
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


def note_seq_to_pdf_separated(noteseq_x, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    separated_by_program = get_program_grouping(noteseq_x)
    mapping = MIDI_PROGRAM_MAPPING
    for program, notes in separated_by_program.items():
        temp_ns = note_seq.NoteSequence()
        for note in notes:
            temp_ns.notes.append(note)
        note_seq_to_pdf(
            temp_ns, 
            os.path.join(output_dir, str(mapping[program]["instrument"]))
        )


def generate_dynamo_transcription_row(prefix, delimiter, bucket_name, metadata={}):
    acc_id = os.path.dirname(prefix)
    title = os.path.basename(prefix)
    song_title, timestamp = title.split(delimiter)
    timestamp = int(timestamp)
    datetime_object = datetime.datetime.fromtimestamp(timestamp)
    date = datetime_object.strftime("%Y-%m-%d")
    return {
        "acc_id": acc_id,
        "transcription_id": title,
        "title": song_title,
        "date": date,
        "metadata": metadata,
        "s3_uri": f"s3://{bucket_name}/{acc_id}/{title}",
    }


def lambda_handler(event, context):
    # get  bucket name and key (file path) from the event
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]  # 'audio-processed-1'
    key = unquote_plus(
        event["Records"][0]["s3"]["object"]["key"]
    )  # 'username/song::timestamp/file.mp3'

    prefix = os.path.dirname(key)  # 'username/song::timestamp'

    if not os.path.exists(GENERATED_OUTPUTS_LOCAL_DIR):
        os.makedirs(GENERATED_OUTPUTS_LOCAL_DIR)

    # construct the path to the audio file
    if not os.path.exists(INPUT_LOCAL_DIR_NAME):
        os.makedirs(INPUT_LOCAL_DIR_NAME)
    audio_file_path = os.path.join(INPUT_LOCAL_DIR_NAME, os.path.basename(key)) # 'input/file.mp3'

    try:
        # Download the audio file from the S3 bucket
        print(">> Downloading input audio...")
        download_audio_file(bucket_name, key, audio_file_path)

        # load model
        print(">> Creating model...")
        inference_model = InferenceModel(MODEL_CHECKPOINT_PATH, MODEL_NAME)

        # load audio
        print(">> Loading input audio...")
        audio, sample_rate = librosa.load(audio_file_path)
        # assert sample_rate == 16000  # TODO: do we need to assert, what happens if it's more/less than 16k

        # run transcription
        print(">> Transcribing...")
        start_time = time.perf_counter()
        est_ns = inference_model(audio)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f">> Initial Transcription elapsed time: {elapsed_time:.2f} seconds")

        # separate output
        print(">> Applying Postprocessing...")
        print(">> >> Fusing redundant instruments...")
        ns_with_fused_instruments = fuse_instruments(est_ns)
        print(">> >> Discarding redundant classes...")
        ns_with_discarded_classes = discard_classes(ns_with_fused_instruments)

        # convert to PDF
        print(">> Generating outputs...")
        note_seq_to_pdf_separated(
            ns_with_discarded_classes, 
            GENERATED_OUTPUTS_LOCAL_DIR
        )
        note_seq_to_pdf(
            ns_with_discarded_classes,
            GENERATED_OUTPUTS_LOCAL_DIR,
        )

        # upload outputs to S3
        print(">> Uploading outputs to S3 bucket...")
        upload_folder_to_s3(
            GENERATED_OUTPUTS_LOCAL_DIR, 
            OUTPUT_BUCKET_NAME, 
            prefix
        )

        # write to dynamo
        write_to_dynamo(
            DYNAMO_TABLE_NAME,
            generate_dynamo_transcription_row(
                prefix=prefix, 
                delimiter=DELIMITER, 
                bucket_name=OUTPUT_BUCKET_NAME
            ),
        )
    except Exception as e:
        print(f"Error: {e}")
        raise e
