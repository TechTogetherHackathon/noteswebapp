import os

from google.cloud import storage

from datetime import datetime
import moviepy.editor as mp

#from google.cloud import speech_v1 as speech
import SpeechRecognition as sr
from os import path
from pydub import AudioSegment


def upload_video(file_name):
    storageCli = storage.Client()
    # get bucket
    bucket = storageCli.get_bucket('transcribevideos')
    blob = bucket.blob(file_name)

    # TODO: Fix this error of AttributeError: 'str' object has no attribute 'tell', needs to save in /tmp file in google cloud function
    blob.upload_from_filename(file_name)

    return


def process_file(file):
    audio_file = "../audio.mp3"
    clip = mp.VideoFileClip(file)
    clip.audio.write_audiofile(audio_file)

    return audio_file


def transcribe_video(mp4_file):
    audio_file_name = process_file(mp4_file)

    sound = AudioSegment.from_mp3(audio_file_name)

    sound.export("audio.wav", format="wav")

    # transcribe audio file
    AUDIO_FILE = "audio.wav"

    # use the audio file as the audio source
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  # read the entire audio file

        print("Transcription: " + r.recognize_google(audio))

    return

#     audio_file = "../audio.ogg"
#     upload_video(audio_file)

#     client = speech.SpeechClient()
#     audio = speech.RecognitionAudio(
#         uri="gs://" + "transcribevideos" + "/" + audio_file)
#     config = speech.RecognitionConfig(
#         encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
#         language_code='en-US',
#         sample_rate_hertz=16000,
#         enable_word_time_offsets=True
#     )
#     operation = client.long_running_recognize(config, audio)

#     if not operation.done():
#         print('Waiting for results...')

#         result = operation.result()

#         results = result.results

#         raw_text_file = open(audio_file + '.txt', 'w+')
#         for result in results:
#             for alternative in result.alternatives:
#                 raw_text_file.write(alternative.transcript + '\n')
#         raw_text_file.close()  # output raw text file of transcription

#         # output .srt formatted version of transcription
#         #format_transcript(results, audio_file)
#     else:
#         return


if __name__ == "__main__":
    file_name = "../Quick sort in 4 minutes.mp4"

    transcribe_video(file_name)
