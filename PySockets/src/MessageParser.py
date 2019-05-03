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

class MessageParser:  # TODO: Complete
    def __init__(self, relay_control): 
        self._relay_control = relay_control
        self._validMessage = {'on':self._relay_control.on,
                              'off':self._relay_control.off,
                              'invert':self._relay_control.invert}
        self._relayPattern = re.compile("^([Rr][1-8])$")  # possibility have a range specified in a config
        # TODO: read the config file for fan names and create dictionary to look up corresponding
        # TODO: self._ fan R1 r1 light red [1]
        # TODO: toggle state with other if on and turn on too?
        # TODO: like red: turns off the white light if on and turns r7 on,
        # TODO: line fans: controls both the r2 & r8,

    def decrypt():  # TODO: do maybe refactor to verify too
        pass

    def parse(self, message):
        message = message.split()
        if (self._relayPattern.match(message[1]) is not None) and message[0] in self._validMessage:
            self._validMessage[message[0]](message[1])
        else:  # if (): # TODO: have a look into the dict and if there is a list call multiple relays
            print(message)    
        if message[0] in self._validMessage:
            self._validMessage[message[0]](message[1])
