from __future__ import print_function
from scapy.all import * 
# sudo apt-get install python-scapy
# sudo -H pip install scapy-python3 --user
import socket
import sys
import signal
from threading import Thread
import re
import RPi.GPIO as GPIO
import urllib2
import datetime

connection = None
sock = None
signal_catcher = None
# TODO: look at workspace.txt for any projects to integrate

class RelayControl:
    def __init__(self):
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        self.GPIO = GPIO
        self._pinList = [2, 3, 4, 17, 27, 23, 10, 9]
        self._buttonList = [ 16, 26 ] # TODO: read from server.confg
        # GPIO pins on the Pi so the first relay is at GPIO pin 2, the 4th is at GPIO pin 17
        self._relay_state = [False] * 8
        for index in range(len(self._pinList)):  # turn off all the relays
            print("GPIO.setup pin:" + str(self._pinList[index]))
            GPIO.setup(self._pinList[index], GPIO.OUT)
            GPIO.output(self._pinList[index], GPIO.HIGH)
        for pin in self._buttonList:  # set button pins to 3.3v
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.RISING, callback=self.button_pressed, bouncetime=1500) #was GPIO.FALLING
    
    def _change_relay_state(self, relay_num, new_state):
        print("Setting relay #", relay_num, "to", new_state)
        
        if new_state:
            self.GPIO.output(self._pinList[int(relay_num)-1], self.GPIO.LOW)  # on
            self._relay_state[int(relay_num)-1] = True
        else: 
            self.GPIO.output(self._pinList[int(relay_num)-1], self.GPIO.HIGH)  # off
            self._relay_state[int(relay_num)-1] = False
    
    def invert(self, relay_num):
        print("invert called")
        self._change_relay_state(relay_num, not self.state(relay_num))

    def on(self, relay_num):
        self._change_relay_state(relay_num, True)

    def off(self, relay_num):
        self._change_relay_state(relay_num, False)

    def all_off(self):
        for index in range(len(self._pinList)):
            self._change_relay_state(index+1, False)

    def state(self, relay_num):
        return self._relay_state[int(relay_num)-1]

    def states(self):
        return self._relay_state
        
    def button_pressed(self, channel):
        print("Button Pressed", channel)
        if channel == 26:
            pass #self.invert(8)
        elif channel == 16: #TODO: invistigate why GPIO 16 triggers 26 rising, either coding error or physical wiring 
            pass #self.invert(2)
    
    def __del__(self):
        print("Cleaning up GPIO")
        GPIO.cleanup()
