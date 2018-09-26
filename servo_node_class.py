#!/usr/bin/python

import pantilthat
import rospy
import json
import time
import string
from std_msgs.msg import String


class Servo(object):
    def __init__(self):
        file_path = __file__.replace("servo_node_class.py","")
        setting_file = open(file_path + "settings.txt",'r')
        js = setting_file.read()
        self.settings = json.loads(js)
        setting_file.close()
        self.servo_step = int(self.settings["servo step"])
        pantilthat.servo_enable(1,True)
        pantilthat.servo_enable(2,True)
        self.v_angle = int(self.settings["default v angle"])
        self.default_v_angle = self.v_angle
        self.p_angle = int(self.settings["default p angle"])
        self.default_p_angle = self.p_angle
        self.c_v_angle = self.v_angle
        self.c_p_angle = self.p_angle
        self.image_width = int(self.settings["image width"])
        self.image_height = int(self.settings["image height"])
        self.pixel_bias = int(self.settings["bias pixels"])
        self.p_coff = 0.05
        self.v_coff = 0.02
        self.rate = 0.05
        #self.delta_p_angle = 0
        #self.delta_c_angle = 0
        self.stop_timer = 0
        
        rospy.init_node('servo_node')
        rospy.Subscriber("command_topic",String,self.servo_move)
        rospy.Subscriber("servo_calibration",String,self.servo_calibration)
        self.servo_drive(int(self.c_p_angle),int(self.c_v_angle))
        
        
    def servo_drive(self,pan,tilt):
        if pan >= 90:
            pan = 90
        if pan <= -90:
            pan = -90
        if tilt >= 90:
            tilt = 90
        if tilt <= -90:
            tilt = -90
        pantilthat.pan(pan)
        pantilthat.tilt(tilt)

    def slow_move(self):
        #if ((time.clock() - self.stop_timer)*10) > 10:
        #    self.p_angle = self.default_p_angle
        #    self.v_angle = self.default_v_angle
        #    self.stop_timer = time.clock()
        
        if ((self.c_p_angle - self.p_angle)>1) or ((self.p_angle - self.c_p_angle) > 1):
            self.c_p_angle = self.c_p_angle + self.rate * (self.p_angle - self.c_p_angle)
            print(self.c_p_angle)
        else:
            self.c_p_angle = self.p_angle
            

        if ((self.c_v_angle - self.v_angle) > 1) or ((self.v_angle - self.c_v_angle) > 1):
            self.c_v_angle = self.c_v_angle + self.rate * (self.v_angle - self.c_v_angle)
            print(self.c_v_angle)
        else:
            self.c_v_angle = self.v_angle

        self.servo_drive(int(self.c_p_angle),int(self.c_v_angle))
        

    def servo_move(self,data):
        #print(str(data))
        data_string = data.data
        data_string = str(data_string).replace("\\","")
        #data_string = data_string.replace("data: ","")
        #data_string = data_string.strip("\"")
        print(data_string)
        comm_dic = json.loads(data_string)
        if comm_dic["command"] == "move":
            if comm_dic["direction"] == "up":
                self.v_angle = self.v_angle - self.servo_step
            elif comm_dic["direction"] == "down":
                self.v_angle = self.v_angle + self.servo_step
            elif comm_dic["direction"] == "left":
                self.p_angle = self.p_angle + self.servo_step
            elif comm_dic["direction"] == "right":
                self.p_angle = self.p_angle - self.servo_step
            else:
                comm_dic["direction"] = ""
            comm_dic["command"] = ""
            #self.servo_drive(self.p_angle,self.v_angle)
        elif comm_dic["command"] == "move to":
            self.p_angle = int(comm_dic["pan"])
            self.v_angle = int(comm_dic["tilt"])
            #self.servo_drive(self.p_angle,self.v_angle)
        elif comm_dic["command"] == "quit":
            pantilthat.servo_enable(1,False)
            pantilthat.servo_enable(2,False)
        elif comm_dic["command"] == "start":
            pantilthat.servo_enable(1,True)
            pantilthat.servo_enable(2,True)
            self.v_angle = int(settings["default v angle"])
            self.p_angle = int(settings["default p angle"])
            #self.servo_drive(self.p_angle,self.v_angle)
        elif comm_dic["command"] == "default":
            self.p_angle = self.default_p_angle
            self.v_angle = self.default_v_angle
        else:
            comm_dic["command"] = ""

    def servo_calibration(self,recv_data):
        self.stop_timer = time.clock()
        comm_dic = json.loads(str(recv_data.data))
        x_center = int(comm_dic["x center"])
        y_center = int(comm_dic["y center"])
        if ((y_center - self.image_height/2) > self.pixel_bias) or ((self.image_height/2 - y_center) > self.pixel_bias): 
            self.v_angle = self.c_v_angle + int(self.v_coff * (y_center - self.image_height/2))
        if ((x_center - self.image_width/2) > self.pixel_bias) or ((self.image_width/2 - x_center) > self.pixel_bias): 
            self.p_angle = self.c_p_angle - int(self.p_coff * (x_center - self.image_width/2))

        if self.v_angle >= 90:
            self.v_angle = 90
        if self.v_angle <= -90:
            self.v_angle = -90
        if self.p_angle >= 90:
            self.p_angle = 90
        if self.p_angle <= -90:
            self.p_angle = -90
        #print("Calibration")
        #self.servo_drive(self.p_angle,self.v_angle)


def servo_node():
    servo = Servo()
    rate = rospy.Rate(100)
    while not rospy.is_shutdown():
        servo.slow_move()
        rate.sleep()


if __name__ == '__main__':
    try:
        servo_node()
    finally:
        pantilthat.servo_enable(1,False)
        pantilthat.servo_enable(2,False)
