import os

from google.cloud import storage

from datetime import datetime
import moviepy.editor as mp

# from google.cloud import speech_v1 as speech
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
from nltk.stem import PorterStemmer
import nltk
import ssl
import io
import nltk
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
from google.cloud import speech


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


def transcribe_video(file_name):
    upload_video(file_name)
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri="gs://transcribevideos/" + file_name)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        language_code="en-US",
        audio_channel_count=2,
        # Enable automatic punctuation
        enable_automatic_punctuation=True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)

    # print(response.results)
    text = ""

    for result in response.results:
        # The first alternative is the most likely one for this portion.
        text += result.alternatives[0].transcript

    f = open("file.txt", "w+")
    f.write(text)
    f.close()
    summ = generate_summary("file.txt", 6)
    results = []
    results.append(text)
    results.append(summ)
    return results


def read_article(file_name):
    file = open(file_name, "r")
    filedata = file.readlines()
    article = filedata[0].split(". ")
    sentences = []

    for sentence in article:
        sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
    sentences.pop()

    return sentences


def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []

    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]

    all_words = list(set(sent1 + sent2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1

    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)


def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2:  # ignore if both are same sentences
                continue
            similarity_matrix[idx1][idx2] = sentence_similarity(
                sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix

def filter_by_keyword(file_name, keyword):
    with open(file_name, 'r') as inF:
        for line in inF:
            if keyword in line:
                print("found it!")
        print("done")

def generate_summary(file_name, top_n):

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    stop_words = stopwords.words('english')
    summarize_text = []

    # Step 1 - Read text anc split it
    sentences = read_article(file_name)

    # Step 2 - Generate Similary Martix across sentences
    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

    # Step 3 - Rank sentences in similarity martix
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)

    # Step 4 - Sort the rank and pick top sentences
    ranked_sentence = sorted(
        ((scores[i], s) for i, s in enumerate(sentences)), reverse=True)

    # avoid out of bounds error by limiting top_n to be max number of sentences in the text
    if top_n > len(sentences):
        top_n = len(sentences)

    for i in range(top_n):
        summarize_text.append(" ".join(ranked_sentence[i][1]))
        summarize = '. '.join(summarize_text)

    f = open("summary.txt", "w+")
    f.write(summarize)
    f.close()
    return summarize


if __name__ == "__main__":

    file_name = 'audio.flac'

    # transcribe_video(file_name)
    filter_by_keyword("file.txt", "mergesort")
    # generate_summary("file.txt", 2)
