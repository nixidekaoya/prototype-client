#!/usr/bin/env python

import json
import rospy
#import pyttsx
import sys
import os
import time
#import festival 
#from espeak import espeak
from std_msgs.msg import String




class Speaker(object):
    def __init__(self):
        self.file_path = __file__.replace("speaker_node.py","")
        self.textfilename = self.file_path + "temp_voice.txt"
        self.wavfilename = self.file_path + "temp_wave.wav"
        self.speak_buff = "hello world"
        #engine = pyttsx.init(driverName = 'espeak' , debug = True)
        rospy.init_node('speaker_node')
        rospy.Subscriber("speaker_text",String,self.speak_buffer)
        self.clock1 = time.clock()
        self.clock2 = time.clock()
    def speak_buffer(self,recv_data):
        self.speak_buff = recv_data.data

    def speak_out(self):
        if self.speak_buff:
            try:
                os.system("pulseaudio --kill")
                os.system("sleep 1")
            except:
                os.system("sleep 1")
            #temp_file = open(self.textfilename,"w")
            speak_text = self.speak_buff
            self.speak_buff = ""
            speak_text = '"' + speak_text + '"'
            print(speak_text)
            #temp_file.write(speak_text)
            #temp_file.close()
            #os.system("text2wave " + self.textfilename + " -F 8000 -o " + self.wavfilename)
            #os.system("aplay -r 8000 -P " + self.wavfilename)
            os.system("espeak " + speak_text + " -p 40 -g 3 -s 160 -v f4")
            os.system("sleep 1")
            #self.clock1 = time.clock()
            #self.clock2 = time.clock()
            #os.system("sleep 5")
            #while (self.clock2 - self.clock1) < 5:
            #    self.clock2 = time.clock()
                #print(str(self.clock2 - self.clock1))
        


    


def speaker_node():
    speaker = Speaker()
    rate = rospy.Rate(0.2)
    #os.system("espeak 'hello world'")
    #os.system("sleep 2")
    while not rospy.is_shutdown():
        speaker.speak_out()
        #rate.sleep()
    #engine.startLoop(True)
    #rospy.spin()


if __name__ == '__main__':
    speaker_node()
