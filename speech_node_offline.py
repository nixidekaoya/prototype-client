#!/usr/bin/env python

import rospy
import time
import json
import pyaudio
import speech_recognition as sr
from std_msgs.msg import String
from audio_common_msgs.msg import AudioData
from pocketsphinx import Decoder,DefaultConfig, get_model_path, get_data_path
from sphinxbase.sphinxbase import *



class SpeechRecognizer(object):
    def __init__(self):
        #print(sr.Microphone.list_microphone_names())
        self.file_path = __file__.replace("speech_node_offline.py","")
        self.wav_file = self.file_path + "record.wav"
        rospy.init_node("speech_node")
        self.ad_pub = rospy.Publisher('audio_data',AudioData,queue_size = 1)
        #self.model_path = get_model_path()
        #self.data_path = get_data_path()
        #change the user keys if possible
        self.r = sr.Recognizer()
        self.r.energy_threshold = 2000
        self.r.dynamic_energy_threshold = False
        self.r.pause_threshold = 0.8
        self.r.phrase_threshold = 0.1
        self.r.non_speaking_duration = 0.3
        self.sampling_rate = 16000
        self.chunk_size = 1024

    def ad_msg_publish(self,ad_msg):
        self.ad_pub.publish(ad_msg)



def speech_node_offline():
    index = 1
    speechrecognizer = SpeechRecognizer()
    for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
        if microphone_name == "Sound Blaster Play! 3: USB Audio (hw:1,0)":
            index = i
            print(index)
    with sr.Microphone(index) as source:
        #speechrecognizer.r.adjust_for_ambient_noise(source,duration = 3)
        while not rospy.is_shutdown():
            #print("Speak something for testing")
            audio = speechrecognizer.r.listen(source)
            #print(audio.sample_rate)
            #print(audio.sample_width)
            #result = ""
            #try:
             #   result = speechrecognizer.r.recognize_sphinx(audio_data = audio, language = "en-US")
             #   print(result)
            #except sr.UnknownValueError:
             #   print("You said nothing!")
            ad_msg = AudioData()
            ad_msg.data = audio.get_wav_data()
            with open(speechrecognizer.wav_file,"wb") as f:
                f.write(audio.get_wav_data())
            print("send audio data")
            speechrecognizer.ad_msg_publish(ad_msg)

if __name__ == '__main__':
    speech_node_offline()
