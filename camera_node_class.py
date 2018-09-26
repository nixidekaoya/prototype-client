#!/usr/bin/python

import rospy
import json
import time
import threading
import picamera
import sys
import io
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage



class Camera(object):
    def __init__(self):
        self.pi_camera = picamera.PiCamera()
        self.pi_camera.vflip = True
        self.pi_camera.hflip = True
        self.pi_camera.framerate = 10
        file_path = __file__.replace("camera_node_class.py","")
        setting_file = open(file_path + "settings.txt",'r')
        js = setting_file.read()
        self.settings = json.loads(js)
        setting_file.close()
        self.timer = 0
        self.previous_timer = 0

        self.image_width = int(self.settings["image width"])
        self.image_height = int(self.settings["image height"])
        self.pi_camera.resolution = (self.image_width,self.image_height)
        self.image_pub = rospy.Publisher('image_stream',CompressedImage,queue_size = 1)
        self.image_pub_tm = rospy.Publisher('image_stream_for_tm',CompressedImage,queue_size = 1)
        #self.image_save_pub = rospy.Publisher('image_save_stream',CompressedImage,queue_size =1)
        self.image_msg = CompressedImage()
        self.image_msg.format = "jpeg"
        rospy.init_node('camera_node')
        #rospy.Subscriber("image_send_save",String,self.send_image)
        rospy.Subscriber("command_topic",String,self.camera_command)

        self.gui_refresh_flag = False
        

    def camera_capture(self):
        if True:
            with io.BytesIO() as image_stream:
                self.timer = time.time() - self.previous_timer
                clock1 = time.time()
                self.pi_camera.capture(image_stream,format = 'jpeg',quality = 100,use_video_port = True)
                self.image_msg.data = image_stream.getvalue()
                self.image_pub_tm.publish(self.image_msg)
                if self.timer > 0.3:
                    self.image_pub.publish(self.image_msg)
                    self.previous_timer = time.time()
                    print("send!")
                    self.timer = 0
                #self.image_counter += 1
                clock2 = time.time()
                print(clock2 - clock1)
            


    def send_image(self,recv_data):
        print("Send image for recognition")
        if recv_data.data == "Ready":
            with io.BytesIO() as image_stream:
                self.pi_camera.capture(image_stream,format = 'jpeg', quality = 40)
                self.image_msg.data = image_stream.getvalue()
                #self.image_save_pub.publish(image_msg)

    def camera_command(self,recv_data):
        data_string = recv_data.data
        data_string = str(data_string).replace("\\","")
        comm_dic = json.loads(data_string)
    
    #print(len(image_stream.getvalue()))
        if comm_dic["command"] == "send":
            self.gui_refresh_flag = True

        elif comm_dic["command"] == "quit":
            self.pi_camera.stop_preview()
            self.pi_camera.close()
            print "bye!"
            sys.exit()
        elif comm_dic["command"] == "stop":
            self.gui_refresh_flag = False
        else:
            i = 1

    def close_camera(self):
        self.pi_camera.close()




def camera_node(camera):
    #input_thread = InputThread()
    #input_thread.start()
    while not rospy.is_shutdown():
        camera.camera_capture()
    #rospy.spin()
    






if __name__ == '__main__':
    camera = Camera()
    try :
        camera_node(camera)
    finally:
        camera.close_camera()
