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

class IRControl: # for air conditioner control,
    '''@note had problems with IR on the pi3 b+ works on pi2 b+ have to get that working first'''
    def __init__(self):  
        pass

    def ac_on(self):
        pass

    def ac_off(self):
        pass

