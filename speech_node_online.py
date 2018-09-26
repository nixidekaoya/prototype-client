#!/usr/bin/env python

import rospy
import time
import json
import pyaudio
import speech_recognition as sr
from std_msgs.msg import String
from pocketsphinx import Decoder,DefaultConfig, get_model_path, get_data_path
from sphinxbase.sphinxbase import *



class SpeechRecognizer(object):
    def __init__(self):
        #print(sr.Microphone.list_microphone_names())
        rospy.init_node("speech_online_node")
        self.sr_pub = rospy.Publisher('sr_result',String,queue_size = 1)
        #self.model_path = get_model_path()
        #self.data_path = get_data_path()
        #change the user keys if possible
        self.microsoft_keys = "def4789dde804b599cd8976b96838a84"
        self.wit_ai_keys = "NA3CDAK3ZSL7XDPK6W54WVWWHRGXDP5P"
        self.ibm_username = "ea5868f4-b31a-486e-98c8-f22eba1343fd"
        self.ibm_password = "1aiOcJrMTEH6"
        self.r = sr.Recognizer()
        self.r.energy_threshold = 1500
        self.r.dynamic_energy_threshold = False
        self.r.pause_threshold = 0.8
        self.r.phrase_threshold = 0.1
        self.r.non_speaking_duration = 0.3
        self.sampling_rate = 16000
        self.chunk_size = 1024

    def recognize_online_test(self,audio):
        result = ""
        clock1 = time.clock()
        try:
            result = self.r.recognize_google(audio_data = audio, language = "en-US", show_all = True)
            print("goole think you said:" + str(result))
        except sr.UnknownValueError:
            print("google: You said nothing!")
        except sr.RequestError:
            print("Cannot access google speech recognition!")
        clock2 = time.clock()
        print("google takes: " + str(clock2 - clock1))
        try:
            result = self.r.recognize_bing(audio_data = audio, key = self.microsoft_keys , language = "en-US", show_all = True)
            print("microsoft think you said:" + str(result))
        except sr.UnknownValueError:
            print("microsoft: You said nothing!")
        except sr.RequestError:
            print("Cannot access microsoft bing speech recognition!")
        clock3 = time.clock()
        print("microsoft takes :" + str(clock3 - clock2))
        try:
            result = self.r.recognize_wit(audio_data = audio, key = self.wit_ai_keys ,show_all = True)
            print("wit ai think you said:" + str(result))
        except sr.UnknownValueError:
            print("wit ai: You said nothing!")
        except sr.RequestError:
            print("Cannot access wit ai speech recognition!")
        clock4 = time.clock()
        print("wit ai takes " + str(clock4 - clock3))
        try:
            result = self.r.recognize_ibm(audio_data = audio, username = self.ibm_username , password = self.ibm_password, language = "en-US", show_all = True)
            print("ibm think you said:" + str(result))
        except sr.UnknownValueError:
            print("ibm: You said nothing!")
        except sr.RequestError:
            print("Cannot access ibm speech recognition!")
        clock5 = time.clock()
        print("ibm takes " + str(clock5 - clock4))
        
            

    def recognize_online(self,audio):
        result = ""
        print("Start recognizing!")
        try:
            result = self.r.recognize_bing(audio_data = audio, key = self.microsoft_keys , language = "en-US")
        except sr.UnknownValueError:
            print("google: You said nothing!")
        except sr.RequestError:
            try:
                result = self.r.recognize_google(audio_data = audio,language = "en-US")
            except sr.UnknownValueError:
                print("microsoft: You said nothing!")
            except sr.RequestError:
                try:
                    result = self.r.recognize_wit(audio_data = audio, key = self.wit_ai_keys)
                except sr.UnknownValueError:
                    print("wit_ai: You said nothing!")
                except sr.RequestError:
                    try:
                        result = self.r.recognize_ibm(audio_data = audio, username = self.ibm_username , password = self.ibm_password, language = "en-US")
                    except sr.UnknownValueError:
                        print("IBM: You said nothing!")
                    except sr.RequestError:
                        pass
        
        if result:
            result = result.lower()
            self.ros_publish(result)


    def ros_publish(self,result):
        publish_string = String()
        publish_string.data = result
        self.sr_pub.publish(publish_string)
        print(result)



def speech_node_online():
    index = 1
    speechrecognizer = SpeechRecognizer()
    for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
        print(microphone_name)
        if microphone_name == "Sound Blaster Play! 3: USB Audio (hw:1,0)":
            print(i)
            index = i
    with sr.Microphone(index) as source:
        #speechrecognizer.r.adjust_for_ambient_noise(source,duration = 3)
        while not rospy.is_shutdown():
            print("Say something for testing!")
            audio = speechrecognizer.r.listen(source = source , phrase_time_limit = 2)
            speechrecognizer.recognize_online(audio)

if __name__ == '__main__':
    speech_node_online()
