import azure.cognitiveservices.speech as sdk
from pydub import AudioSegment
import json
import os
import preprocess


# Making sure needed directories exist
def check_dirs():
    if not os.path.exists('source'):
        os.makedirs('source')
    if not os.path.exists('result'):
        os.makedirs('result')


# Getting user config
def read_config():
    if not os.path.isfile('config'):
        preprocess.Configurator()
    with open("config", "r") as config:
        my_key = config.readline()[:-1]
        my_region = config.readline()[:-1]
        my_language = config.readline()
    return my_key, my_region, my_language


# Asking user for file to be processed
def get_filename():
    while True:
        input_file = input("Enter a name of file to process: ")
        try:
            _check = AudioSegment.from_wav(proc_path(input_file))
            return input_file
        except:
            print("Incorrect filename")


# Splitting file to smaller parts for more fluent sdk usage
def split_to_shorter(input_file, split_time):
    loaded_file = AudioSegment.from_wav(proc_path(input_file))
    file_left_ms = loaded_file.duration_seconds * 1000
    start_time = 0
    split_index = 1
    split_list = []

    while file_left_ms > split_time:
        split = loaded_file[start_time:start_time + split_time]
        start_time += split_time
        file_left_ms -= split_time
        filename = input_file[:-4] + "-" + str(split_index) + ".wav"
        split.export(proc_path(filename), format="wav")
        split_list.append(filename)
        split_index += 1

    split = loaded_file[start_time:]
    filename = input_file[:-4] + "-" + str(split_index) + ".wav"
    split.export(proc_path(filename), format="wav")
    split_list.append(filename)
    print("Files after split: " + str(split_index) + ", Single file length: " + str(split_time / 1000) + "s")
    return split_list


# Path with the file being processed
def proc_path(name):
    return "source/" + name


# Path with the result file
def res_path(name):
    return "result/" + name


# Converting recognition result to ms
def align_to_ms(words):
    for word in words:
        word['Offset'] /= 10000
        word['Duration'] /= 10000
    return words


# Using external server for speech recognition
def recognize_speech(input_file, my_key, my_region, my_language):
    speech_config = sdk.SpeechConfig(subscription=my_key, region=my_region, speech_recognition_language=my_language)
    speech_config.request_word_level_timestamps()
    audio_input = sdk.AudioConfig(filename=proc_path(input_file))
    speech_recognizer = sdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
    print("Processing data on external server...")
    result = speech_recognizer.recognize_once_async().get()

    return result.json


# Getting the best recognition result
def get_best(operational_json):
    operational_data = json.loads(operational_json)
    if operational_data["RecognitionStatus"] == "Success":
        print("Data correct")
    else:
        print("Data incorrect")
        exit("Error")
    confidences_n_best = [item['Confidence'] for item in operational_data['NBest']]
    best_index = confidences_n_best.index(max(confidences_n_best))
    words = operational_data['NBest'][best_index]['Words']
    print("Best match: " + operational_data['NBest'][best_index]['Lexical'])
    return words


# Writing transcription of segment to text file
def text_to_file(text, filename):
    with open(res_path(filename + ".txt"), "w") as textFile:
        textFile.write(text)


# Splitting files without cutting words and exporting results
def make_transcription(words, input_file, segment_duration_ms):
    start_time = words[0]['Offset']
    loaded_file = AudioSegment.from_wav(proc_path(input_file))
    segment_index = 1
    segment_text = ""
    for word in words:
        segment_text += word['Word'] + " "
        if word['Offset'] - start_time > segment_duration_ms or words.index(word) == len(words) - 1:

            filename = input_file[:-4] + '-' + str(segment_index)
            print("Segment " + str(segment_index) + ": " + segment_text[:-1])
            text_to_file(segment_text[:-1], filename)
            segment_text = ""

            segment = loaded_file[start_time:(word['Offset'] + word['Duration'])]
            if words.index(word) != len(words) - 1:
                start_time = words[words.index(word) + 1]['Offset']
            segment.export(res_path(filename + ".wav"), format="wav")
            segment_index += 1
