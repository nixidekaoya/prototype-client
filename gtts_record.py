#!/usr/bin/env python

import json
import os
import time
import random
from gtts import gTTS


file_path = __file__.replace("gtts_record.py","")
sound_file_path = file_path + "sound/"
sound_txt_path = sound_file_path + "sound.txt"



if __name__ == '__main__':
    sound_txt_file = open(sound_txt_path,'r')
    for line in sound_txt_file:
        line = line.replace('\n','')
        save_file_name = sound_file_path + line + ".mp3"
        tts = gTTS(line,lang = 'en')
        tts.save(save_file_name)
        print(line + " Complete!")
    sound_txt_file.close()
