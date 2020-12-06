from flask import Flask, request, render_template,jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from transcribe import *
import json

app = Flask(__name__)
def do_something(text1,text2):
   text1 = text1.upper()
   text2 = text2.upper()
   combine = text1 + text2
   return combine
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/transcribe/<data>')
def show_results(data):
    print(str(data))
    # summary = request.form['summary']
    return render_template("secondPage.html")

@app.route('/upload', methods=['GET','POST'])
def my_form_post():
    print(request.form['input'])
    file_name = 'audio.flac'

    results = []
    results = transcribe_video(file_name)
    return jsonify(transcript=results[0], summary=results[1])
    # return jsonify(summary=summary)
if __name__ == '__main__':
    app.run(debug=True)
