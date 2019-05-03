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

class DropboxListener:
    # TODO: test current except code works(no network connectivity set all to false)
    def __init__(self, relay_control): 
        self._relay_control = relay_control
        self.page_url = 'https://carter.page.link/relayState'
        self.page = []
        try:
            self._updated_page = urllib2.urlopen(urllib2.Request(self.page_url)).read().replace('\r', '').split('\n')
        except Exception, e:
            print("File not available yet",str(e))  # wait and call init again and have a count of inits to stop at
            self._updated_page = [False]*9  # sets all relay states to off

    def run(self):     
        while self._updated_page[8] != 'stop':
            ''' if I have to remotely kill the DropboxListener, 
                will not start back up until reboot, 
                TODO: turning all the relays off and killing the process
                TODO: check button state
            '''
            try:
                if self.page != self._updated_page:
                    self.page = self._updated_page
                    print('Dropbox update:',datetime.datetime.now())
                    for index in range(8):
                        if int(self.page[index].split('::')[1]) == 1: #0/1 off/on line would look like '12v fan :: 1'
                            self._relay_control.on(index+1)
                        else: 
                            self._relay_control.off(index+1)
                        time.sleep(.5)
                    print('-------------------------')
                time.sleep(.1)
                self._updated_page = urllib2.urlopen(urllib2.Request(self.page_url)).read().replace('\r', '').split('\n')
            except Exception, e:
                print("Something borked stopping \"",str(e),"\"")
        print('Dropbox Stop Code Received')
