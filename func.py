import azure.cognitiveservices.speech as sdk
from pydub import AudioSegment
import json
import os
import preprocess
import ui


# Reading/creating program config
def read_config():
    if not os.path.isfile('config'):
        preprocess.Configurator()
    with open("config", "r") as config:
        my_key = config.readline()[:-1]
        my_region = config.readline()[:-1]
        my_language = config.readline()
    return my_key, my_region, my_language


# Getting the best recognition result
def get_best(operational_json):
    operational_data = json.loads(operational_json)
    if operational_data["RecognitionStatus"] != "Success":
        ui.hard_error(operational_data['RecognitionStatus'])
    confidences_n_best = [item['Confidence'] for item in operational_data['NBest']]
    best_index = confidences_n_best.index(max(confidences_n_best))
    words = operational_data['NBest'][best_index]['Words']
    return words


# Converting recognition result to ms
def align_to_ms(words):
    for word in words:
        word['Offset'] /= 10000
        word['Duration'] /= 10000
    return words


class Sound:
    def __init__(self, in_path, out_path):
        self.file_data = AudioSegment.from_wav(in_path)
        self.file_name = in_path.join(in_path.split('/')[-1:])
        self.destination = out_path
        self.key, self.region, self.language = read_config()

    # Splitting file to smaller parts for more fluent sdk usage
    def split_to_shorter(self, split_time):
        file_left_ms = self.file_data.duration_seconds * 1000
        start_time = 0
        split_index = 1
        split_list = []

        while file_left_ms > split_time:
            split = self.file_data[start_time:start_time + split_time]
            start_time += split_time
            file_left_ms -= split_time
            filename = self.file_name[:-4] + "-" + str(split_index) + ".wav"
            split.export(self.destination + '/' + filename, format="wav")
            split_list.append(filename)
            split_index += 1

        split = self.file_data[start_time:]
        filename = self.file_name[:-4] + "-" + str(split_index) + ".wav"
        split.export(self.destination + '/' + filename, format="wav")
        split_list.append(filename)
        ui.split_message(split_index, split_time)
        return split_list

    # Using external server for speech recognition
    def recognize_speech(self, filename):
        speech_config = sdk.SpeechConfig(subscription=self.key, region=self.region,
                                         speech_recognition_language=self.language)
        speech_config.request_word_level_timestamps()
        audio_input = sdk.AudioConfig(filename=self.destination + '/' + filename)
        speech_recognizer = sdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
        result = speech_recognizer.recognize_once_async().get()
        return result.json

    # Writing transcription of segment to text file
    def text_to_file(self, text, filename):
        with open(self.destination + '/' + filename + ".txt", "w") as textFile:
            textFile.write(text)

    # Splitting files without cutting words and exporting results
    def make_transcription(self, words, input_file, segment_duration_ms):
        start_time = words[0]['Offset']
        loaded_file = AudioSegment.from_wav(self.destination + '/' + input_file)
        segment_index = 1
        segment_text = ""
        for word in words:
            segment_text += word['Word'] + " "
            if word['Offset'] - start_time > segment_duration_ms or words.index(word) == len(words) - 1:

                filename = input_file[:-4] + '-' + str(segment_index)
                self.text_to_file(segment_text[:-1], filename)
                segment_text = ""

                segment = loaded_file[start_time:(word['Offset'] + word['Duration'])]
                if words.index(word) != len(words) - 1:
                    start_time = words[words.index(word) + 1]['Offset']
                segment.export(self.destination + '/' + filename + ".wav", format="wav")
                segment_index += 1

    # Deleting intermediary files
    def clean_directory(self, file):
        os.remove(self.destination + '/' + file)
