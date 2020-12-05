import os

from google.cloud import storage
from google.cloud import videointelligence
from datetime import datetime
import moviepy.editor as mp

#from google.cloud import speech_v1 as speech
# import SpeechRecognition as sr
from os import path
#from pydub import AudioSegment


def upload_video(file_name):
    storageCli = storage.Client()
    # get bucket
    bucket = storageCli.get_bucket('transcribevideos')
    blob = bucket.blob(file_name)

    # TODO: Fix this error of AttributeError: 'str' object has no attribute 'tell', needs to save in /tmp file in google cloud function
    blob.upload_from_filename(file_name)

    return


# def process_file(file):
#     audio_file = "../audio.mp3"
#     clip = mp.VideoFileClip(file)
#     clip.audio.write_audiofile(audio_file)

#     return audio_file

def transcribe_video(file_name):
    upload_video(file_name)
    startTime = datetime.now()
    """Transcribe speech from a video stored on GCS."""
    video_client = videointelligence.VideoIntelligenceServiceClient()
    features = [videointelligence.Feature.SPEECH_TRANSCRIPTION]

    config = videointelligence.SpeechTranscriptionConfig(
        language_code="en-US", enable_automatic_punctuation=True
    )
    video_context = videointelligence.VideoContext(
        speech_transcription_config=config
    )

    operation = video_client.annotate_video(
        request={
            "features": features,
            "input_uri": "gs://transcribevideos/../Quick sort in 4 minutes.mp4",
            "video_context": video_context,
        }
    )

    print("\nProcessing video for speech transcription.")

    result = operation.result(timeout=30000)

    annotation_results = result.annotation_results[0]
    print(annotation_results)

    for speech_transcription in annotation_results.speech_transcriptions:

        # The number of alternatives for each transcription is limited by
        # SpeechTranscriptionConfig.max_alternatives.
        # Each alternative is a different possible transcription
        # and has its own confidence score.
        for alternative in speech_transcription.alternatives:
            print("Alternative level information:")

            print("Transcript: {}".format(alternative.transcript))
            print("Confidence: {}\n".format(alternative.confidence))

            print("Word level information:")
            for word_info in alternative.words:
                word = word_info.word
                start_time = word_info.start_time
                end_time = word_info.end_time
                print(
                    "\t{}s - {}s: {}".format(
                        start_time.seconds + start_time.microseconds * 1e-6,
                        end_time.seconds + end_time.microseconds * 1e-6,
                        word,
                    )
                )
    return


if __name__ == "__main__":
    file_name = "../Quick sort in 4 minutes.mp4"

    transcribe_video(file_name)
