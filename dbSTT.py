import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
import json
import os


#Getting user config
def read_config():
    with open("config", "r") as config:
        key = config.readline()[:-1]
        region = config.readline()[:-1]
        language = config.readline()
    return key, region, language


#Asking user for file to be processed
def get_filename():
    while True:
        inputFile = input("Enter a name of file to process: ")
        try:
            _check = AudioSegment.from_wav(proc_path(inputFile))
            return inputFile
        except:
            print("Incorrect filename")


#Splitting file to smaller parts for more fluent speechsdk usage
def split_to_shorter(inputFile, splitTime):
    loadedFile = AudioSegment.from_wav(proc_path(inputFile))
    fileLeftMs = loadedFile.duration_seconds * 1000
    startTime = 0
    splitIndex = 1
    splitList = []

    while fileLeftMs > splitTime:
        split = loadedFile[startTime:startTime + splitTime]
        startTime += splitTime
        fileLeftMs -= splitTime
        filename = inputFile[:-4] + "-" + str(splitIndex) + ".wav"
        split.export(proc_path(filename), format="wav")
        splitList.append(filename)
        splitIndex += 1

    split = loadedFile[startTime:]
    filename = inputFile[:-4] + "-" + str(splitIndex) + ".wav"
    split.export(proc_path(filename), format="wav")
    splitList.append(filename)
    print("Quantity of files after split: " + str(splitIndex) + ", Single file length: " + str(splitTime/1000) + "s")
    return splitList


#Path with the file being processed
def proc_path(name):
    return "source/" + name


#Path with the result file
def res_path(name):
    return "result/" + name


#Converting recognition result to miliseconds
def align_to_ms(words):
    for word in words:
        word['Offset'] /= 10000
        word['Duration'] /= 10000
    return words


#Using external server for speech recognition
def recognize_speech(inputFile, key, reg, lang):
    speech_config = speechsdk.SpeechConfig(subscription=key, region=reg, speech_recognition_language=lang)
    speech_config.request_word_level_timestamps()
    audio_input = speechsdk.AudioConfig(filename=proc_path(inputFile))
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
    print("Processing data on external server...")
    result = speech_recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Speech recognition successful")
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("Speech can't be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech recognition cancelled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

    return result.json


#Getting the best recognition result
def get_best(operationalJson):
    operationalData = json.loads(operationalJson)
    if operationalData["RecognitionStatus"] == "Success":
        print("Data correct")
    else:
        print("Data incorrect")
        exit(error)
    confidencesNBest = [item['Confidence'] for item in operationalData['NBest']]
    bestIndex = confidencesNBest.index(max(confidencesNBest))
    words = operationalData['NBest'][bestIndex]['Words']
    print("Best match: " + operationalData['NBest'][bestIndex]['Lexical'])
    return words


#Writing transcription of segment to textfile
def text_to_file(text, filename):
    with open(res_path(filename + ".txt"), "w") as textFile:
        textFile.write(text)


#Splitting files without cutting words and exporting results
def make_transcription(words, inputFile, segmentDurationMs):
    startTime = words[0]['Offset']
    loadedFile = AudioSegment.from_wav(proc_path(inputFile))
    segmentIndex = 1
    segmentText = ""
    for word in words:
        segmentText += word['Word'] + " "
        if word['Offset'] - startTime > segmentDurationMs or words.index(word) == len(words) - 1:

            filename = inputFile[:-4] + '-' + str(segmentIndex)
            print("Segment " + str(segmentIndex) + ": " + segmentText[:-1])
            text_to_file(segmentText[:-1], filename)
            segmentText = ""

            segment = loadedFile[startTime:(word['Offset'] + word['Duration'])]
            if words.index(word) != len(words) - 1:
                startTime = words[words.index(word) + 1]['Offset']
            segment.export(res_path(filename + ".wav"), format = "wav")
            segmentIndex += 1


#-----------------------------------------------------------------------------------------------------------------------------


key, region, language = read_config()
speechFile = get_filename()
#Second arg - duration of file processed by speechsdk [ms]
splitFiles = split_to_shorter(speechFile, 15000)

for file in splitFiles:
    resultJson = recognize_speech(file, key, region, language)
    resultWords = get_best(resultJson)
    #Second arg - minimal duration of result file [ms]
    make_transcription(align_to_ms(resultWords), file, 5000)
    os.remove(proc_path(file))
    print("\n")
os.remove(proc_path(speechFile))
