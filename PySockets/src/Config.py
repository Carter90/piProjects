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

class Config:
    def __init__(self):  # TODO: move all the ConfigParser code here
        self.buttons = dict()
        pass
