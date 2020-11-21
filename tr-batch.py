import os
import azure.cognitiveservices.speech as speechsdk
from pathlib import Path
from shutil import copyfile

service_region = "westus"
speech_key = None

try:
    with open('subscription.key') as key_file:
            speech_key = key_file.read().rstrip('\n\r')
except:
    print("Error reading subscription key file!")
    exit(1)

if speech_key is None:
    print("Subscription key is empty!")
    exit(1)

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

src_dir_str = "./src_wav"
res_dir_str = "./res_wav"
tr_file_str = "./transcripts.txt"

src_dir = os.fsencode(src_dir_str)
Path(res_dir_str).mkdir(parents=True, exist_ok=True)

tr_file = open(tr_file_str,"w") 

format = 1

for file in os.listdir(src_dir):
     filename = os.fsdecode(file)
     filepath = src_dir_str + "/" + filename
     if filename.endswith(".wav"):
         print(filepath)
         audio_input = speechsdk.AudioConfig(filename=filepath)
         speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
         result = speech_recognizer.recognize_once()
         if result.reason == speechsdk.ResultReason.RecognizedSpeech:
             print("Recognized: {}".format(result.text))
             if format == 1:
                tr_file.write(filename[:-4] + '\t' + result.text + '\n')
             if format == 2:
                tr_file.write("( " + filename[:-4] + ' "' + result.text + '" )' + '\n')
             copyfile(filepath, res_dir_str + "/" + filename)
         elif result.reason == speechsdk.ResultReason.NoMatch:
             print("No speech could be recognized: {}".format(result.no_match_details))
         elif result.reason == speechsdk.ResultReason.Canceled:
             cancellation_details = result.cancellation_details
             print("Speech Recognition canceled: {}".format(cancellation_details.reason))
             if cancellation_details.reason == speechsdk.CancellationReason.Error:
                 print("Error details: {}".format(cancellation_details.error_details))
tr_file.close()