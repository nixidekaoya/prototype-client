#!/usr/bin/python

import rospy
import json
import time
import threading
import picamera
import sys
import io
import cv2
from cv_bridge import CvBridge
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage


class LocalTemplateMatching(object):
    def __init__(self):
        file_path = __file__.replace("image_process_node_tm.py","")
        setting_file = open(file_path + "settings.txt",'r')
        js = setting_file.read()
        self.settings = json.loads(js)
        setting_file.close()
        self.image_width = int(self.settings["image width"])
        self.image_height = int(self.settings["image height"])
        self.template = ""
        self.image = ""
        self.template_width = 0
        self.template_height = 0
        self.template_find_w = 40
        self.template_find_h = 40
        self.x_center = 0
        self.y_center = 0
        self.threshold = 0.1
        self.template_matching_method = cv2.TM_SQDIFF_NORMED
        self.cvbr = CvBridge()
        rospy.init_node('image_process_node')
        self.servo_calibration_pub = rospy.Publisher("servo_calibration",String,queue_size = 1)
        rospy.Subscriber("image_stream_for_tm",CompressedImage,self.image_receive)
        rospy.Subscriber("template_image",CompressedImage,self.template_receive)
        rospy.Subscriber("clear_template",String,self.clear_template)
        rospy.Subscriber("",String,self.receive_center)
        

    def receive_center(self,msg):
        msg_json = json.loads(msg.data) 
        self.x_center = int(msg_json["x center"])
        self.y_center = int(msg_json["y center"])

        
    def template_receive(self,template_image):
        self.template = self.cvbr.compressed_imgmsg_to_cv2(template_image)
        self.template_width = self.template.shape[1]
        self.template_height = self.template.shape[0]

    def clear_template(self,msg):
        if msg.data == "clear":
            self.template = ""
            self.template_width = 0
            self.template_height = 0
            self.x_center = 0
            self.y_center = 0

    def image_receive(self,image):
        self.image = self.cvbr.compressed_imgmsg_to_cv2(image)
        if self.template != "":
            if self.x_center != 0 and self.y_center != 0:
                send_json = {}
                send_json["x center"] = x_center
                send_json["y center"] = y_center
                send_buff = json.dumps(send_json)
                self.servo_calibration_pub.publish(send_buff)
                time1 = time.time()
                x_old_center = self.x_center
                y_old_center = self.y_center
                local_left = int(x_old_center - self.template_width/2 - self.template_find_w)
                if local_left < 0:
                    local_left = 0:
                local_right = int(x_old_center + self.template_width/2 + self.template_find_w)
                if local_right >= self.image_width:
                    local_right = self.image_width - 1
                local_up = int(y_old_center - self.template_height/2 - self.template_find_h)
                if local_up < 0 :
                    local_up = 0
                local_down = int(y_old_center + self.template_height/2 + self.template_find_h)
                if local_down >= self.image_height:
                    local_down = self.image_height - 1
                local_image = self.image[local_up:local_down,local_left:local_right]
                res = cv2.matchTemplate(local_image,self.template,self.template_matching_method)
                min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(res)
                time2 = time.time() - time1
            
                print(time2)
                
                #print(min_val)
                if min_val < self.threshold:
                    x_center = int(local_up + min_loc[0] + self.template_width/2)
                    y_center = int(local_down + min_loc[1] + self.template_height/2)
                    print((x_center,y_center))
                else:
                    x_center = 0
                    y_center = 0
                
                
        


def image_process_node(image_process):
    rospy.spin()
    

if __name__ == '__main__':
    image_process = LocalTemplateMatching()
    image_process_node(image_process)
