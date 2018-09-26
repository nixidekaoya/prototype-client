#!/usr/bin/env python

import json
import rospy
import time
import os
import random
from std_msgs.msg import String

class Speaker(object):
    def __init__(self):
        self.file_path = __file__.replace("speaker_node_record_gtts.py","")
        self.sound_path = self.file_path + "sound/"
        rospy.init_node('speaker_node_gtts_record')
        rospy.Subscriber("speaker_json",String,self.speak_buffer)
        speak_object = "book"
        self.speak_file_path = self.sound_path
        self.speak_file_name = self.sound_path + '"Hello.mp3"'
    def speak_buffer(self,recv_data):
        speak_json = json.loads(recv_data.data)
        print(speak_json)
        if speak_json["speak"] == "ask":
            speak_object = speak_json["object"]
            speak_object = speak_object.replace(" ","_")
            random_num = random.randint(1,3)
            self.speak_file_name = self.speak_file_path + speak_object + "_" + str(random_num) + ".mp3"
        elif speak_json["speak"] == "color":
            speak_color = speak_json["color"]
            self.speak_file_name = self.speak_file_path + "color_" + speak_color + ".mp3"
        elif speak_json["speak"] == "greeting":
            now = time.localtime()
            hour = now.tm_hour
            if hour < 12:
                self.speak_file_name = self.speak_file_path + "Goodmorning.mp3"
            elif hour < 18:
                self.speak_file_name = self.speak_file_path + "Goodafternoon.mp3"
            elif hour < 24:
                self.speak_file_name = self.speak_file_path + "Goodevening.mp3"
        elif speak_json["speak"] == "like response":
            random_num = random.randint(1,3)
            self.speak_file_name = self.speak_file_path + "response_like_" + str(random_num) + ".mp3"
        elif speak_json["speak"] == "dislike response":
            random_num = random.randint(1,3)
            self.speak_file_name = self.speak_file_path + "response_dislike_" + str(random_num) + ".mp3"
        elif speak_json["speak"] == "blind response":
            random_num = random.randint(1,3)
            self.speak_file_name = self.speak_file_path + "response_blind_" + str(random_num) + ".mp3"
        elif speak_json["speak"] == "person":
            random_num = random.randint(1,2)
            if random_num == 1:
                self.speak_file_name = self.speak_file_path + '"There is a person over there.mp3"'
            elif random_num == 2:
                self.speak_file_name = self.speak_file_path + '"There is a person in front of you.mp3"'
        elif speak_json["speak"] == "hello":
            self.speak_file_name = self.speak_file_path + "Hello.mp3"
        else:
            self.speak_file_name = ""

    def speak_out(self):
        if self.speak_file_name:
            try:
                os.system("pulseaudio --kill")
                os.system("sleep 0.3")
            except:
                os.system("sleep 0.1")
            os.system("play " + self.speak_file_name)
            #os.system("sleep 1")
            #print(self.speak_file_name)
            self.speak_file_name = ""

                

def speaker_node():
    speaker = Speaker()
    while not rospy.is_shutdown():
        speaker.speak_out()

    
if __name__ == '__main__':
    speaker_node()
