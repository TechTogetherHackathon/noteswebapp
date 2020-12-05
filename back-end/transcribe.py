import os

from google.cloud import storage

from datetime import datetime
import moviepy.editor as mp

#from google.cloud import speech_v1 as speech
import speech_recognition as sr
from os import path
from pydub import AudioSegment
from pydub.silence import split_on_silence
import ffmpeg
import nltk
from nltk.corpus import stopwords
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize


paragraph = "Calgary remains the centre of the province’s coronavirus outbreak, with 378 (61 per cent) of Alberta’s case coming in the AHS Calgary zone, including 325 cases within Calgary’s city limits. The Edmonton zone has 22 per cent of cases, the second-most in the province. More than 42,500 Albertans have now been tested for COVID-19, meaning nearly one in every 100 Albertans have received a test. About 1.5 per cent of those tests have come back positive. Rates of testing in Alberta jolted back up on Friday, with more than 3,600 conducted — the most yet in a single day. The surge followed one of Alberta’s lowest testing days Thursday, as the province shifted its testing focus away from returning travellers and towards health-care workers and vulnerable populations, including those in hospital or living in continuing care facilities."


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
    r = sr.Recognizer()
    harvard = sr.AudioFile('test.wav')
    with harvard as source:
        audio = r.record(source)

    text = r.recognize_google(audio, language='en-US')
    print(text)
    text = paragraph
    # Tokenizing the text
    stopWords = set(stopwords.words("english"))
    words = word_tokenize(text)

    # Creating a frequency table to keep the
    # score of each word

    freqTable = dict()
    for word in words:
        word = word.lower()
        if word in stopWords:
            continue
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1

    # Creating a dictionary to keep the score
    # of each sentence
    sentences = sent_tokenize(text)
    sentenceValue = dict()

    for sentence in sentences:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                if sentence in sentenceValue:
                    sentenceValue[sentence] += freq
                else:
                    sentenceValue[sentence] = freq

    sumValues = 0
    for sentence in sentenceValue:
        sumValues += sentenceValue[sentence]

    # Average value of a sentence from the original text

    average = int(sumValues / len(sentenceValue))

    # Storing sentences into our summary.
    summary = ''
    for sentence in sentences:
        if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)):
            summary += " " + sentence
    print(summary)


if __name__ == "__main__":
    file_name = "../Quick sort in 4 minutes.mp4"

    transcribe_video(file_name)
