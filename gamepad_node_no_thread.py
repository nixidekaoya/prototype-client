#!/usr/bin/python

import usb
import time
import sys
import json
import rospy
from std_msgs.msg import String
        

class GamePad(object):
    def __init__(self):
        rospy.init_node('gamepad_node')
        self.command_pub = rospy.Publisher('command_topic',String,queue_size = 1)
        self.sr_result_pub = rospy.Publisher('sr_result',String,queue_size = 1)
        self.speaker_pub = rospy.Publisher('speaker_json',String,queue_size = 1)
        self.start_button = 0x00
        self.select_button = 0x01
        self.left_button = 0x02
        self.right_button = 0x03
        self.up_button = 0x04
        self.down_button = 0x05
        self.x_button = 0x06
        self.y_button = 0x07
        self.a_button = 0x08
        self.b_button = 0x09
        self.l_button = 0x0A
        self.r_button = 0x0B
        self.default_button = 0xFF
        self.button = self.default_button
        self.idvendor = 0x0810
        self.idproduct = 0xe501
        self.default_data = [1,128,128,127,127,15,0,0]
        self.data = self.default_data
        self.dev = usb.core.find(idVendor = self.idvendor , idProduct = self.idproduct)
        self.default_flag = True
        #print(self.dev)
        if self.dev:
            self.ep = self.dev[0][(0,0)][0]
            self.size = self.ep.wMaxPacketSize
            #print(self.ep)
            #print(self.size)
            try:
                if self.dev.is_kernel_driver_active(0) == True:
                    self.dev.detach_kernel_driver(interface = 0)
                    usb.util.claim_interface(self.dev,interface = 0)
                    print("Gamepad Start!")
            except:
                print("GamePad Ready!")
        else:
            print("GamePad Not Found!!!")
            sys.exit()

    def ros_publish(self,publisher,content):
        json_send = json.dumps(content)
        publisher.publish(json_send)
        print(json_send)

    def run_gamepad(self):
        self.data = self.ep.read(self.size, timeout = 5000)
        #print(self.usb_data)
        self.check_default()
        #print(self.default_flag)
        if self.default_flag == False:
            self.active_button()
            self.buttons()
            while self.default_flag  == False:
                self.data = self.ep.read(self.size, timeout = 5000)
                self.check_default()

    def check_default(self):
        for i in range(8):
            if self.data[i] != self.default_data[i]:
                self.default_flag = False
                break
            else:
                self.default_flag = True
        

    def release_gamepad(self):
        if self.dev:
            try:
                usb.util.release_interface(self.dev,0)
                self.dev.attach_kernel_driver(0)
            except:
                return

    def active_button(self):
        if int(self.data[6]) == 32:
            self.button = self.start_button
        elif int(self.data[6]) == 16:
            self.button = self.select_button
        elif int(self.data[6]) == 1:
            self.button = self.l_button
        elif int(self.data[6]) == 2:
            self.button = self.r_button
        elif int(self.data[4]) == 0:
            self.button = self.up_button
        elif int(self.data[4]) == 255:
            self.button = self.down_button
        elif int(self.data[3]) == 0:
            self.button = self.left_button
        elif int(self.data[3]) == 255:
            self.button = self.right_button
        elif int(self.data[5]) == 31:
            self.button = self.x_button
        elif int(self.data[5]) == 47:
            self.button = self.a_button
        elif int(self.data[5]) == 143:
            self.button = self.y_button
        elif int(self.data[5]) == 79:
            self.button = self.b_button
        else:
            self.button = self.default_button
        #print(self.button)

    def buttons(self):
        if self.button != self.default_button:
            command = {}
            if self.button == self.start_button:
                command["command"] = "send"
                self.ros_publish(publisher = self.command_pub,content = command)
            elif self.button == self.select_button:
                command["command"] = "stop"
                self.ros_publish(publisher = self.command_pub,content = command)
            elif self.button == self.up_button:
                command["command"] = "move"
                command["direction"] = "up"
                self.ros_publish(publisher = self.command_pub,content = command)
            elif self.button == self.down_button:
                command["command"] = "move"
                command["direction"] = "down"
                self.ros_publish(publisher = self.command_pub,content = command)
            elif self.button == self.left_button:
                command["command"] = "move"
                command["direction"] = "left"
                self.ros_publish(publisher = self.command_pub,content = command)
            elif self.button == self.right_button:
                command["command"] = "move"
                command ["direction"] = "right"
                self.ros_publish(publisher = self.command_pub,content = command)
            elif self.button == self.y_button:
                self.sr_result_pub.publish("yes")
            elif self.button == self.a_button:
                self.sr_result_pub.publish("no")
            elif self.button == self.x_button:
                self.sr_result_pub.publish("which one")
            elif self.button == self.b_button:
                self.sr_result_pub.publish("what")
            elif self.button == self.l_button:
                command["command"] = "default"
                self.ros_publish(publisher = self.command_pub,content = command)
            elif self.button == self.r_button:
                command["speak"] = "hello"
                self.ros_publish(publisher = self.speaker_pub,content = command)
            else:
                print("Some bugs here!")
            self.button = self.default_button
                
                
                
        


def gamepad_node(gamepod):
    while not rospy.is_shutdown():
        gamepad.run_gamepad()
        
        



if __name__ == '__main__':
    gamepad = GamePad()

    try:
        gamepad_node(gamepad)
    finally:
        print("over")
        #usbthread._stop_event.set()
        gamepad.release_gamepad()
        
