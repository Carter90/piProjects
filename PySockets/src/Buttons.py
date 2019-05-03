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
class Buttons:
    def __init__(self, relay_control):
        global config
        self._relay_control = relay_control
        print(sys.version_info[0])
        if sys.version_info[0] >= 3:  # ConfigParser changed to configparser in python 3
            python3 = True
            import configparser  # 3
            config = configparser.ConfigParser()  # 3
        else: 
            python3 = False
            import ConfigParser  # 2
            config = ConfigParser.ConfigParser()  # 2
        config.read('/home/carter/relay/PySockets/server.confg')  # TODO: change path based on location
        # TODO: Strip whitespace maybe needed

        if config.has_section('Buttons'):
            # format example: "cheezit  =     00:00:00:00:00:00, fans"
            self.buttons = {macAOpp.split(',')[0]:(name,macAOpp.split(',')[1]) for name, macAOpp
                            in config.items('Buttons')}
            # keys are the mac adress, value is the name of the button
            print(self.buttons)
            # TODO: test if section exists but has not elements
        else: 
            self.buttons = dict()
            print("Empty config")

    def arp_detect(self, pkt):
            if pkt.haslayer(ARP) and pkt[ARP].op == 1:  # network request
                # print("seen arp from: ",pkt[ARP].hwsrc)
                if pkt[ARP].hwsrc in self.buttons:
                    print(self.buttons[pkt[ARP].hwsrc]) # prints mac address and desired action
                    # TODO: possibly have a field in the config for the action send to the parcer
                    self._relay_control.invert(2) # TODO: look at self.buttons[pkt[ARP].hwsrc][1] for action
                    self._relay_control.invert(8)

    def sniffer(self):
        print('Dash Button Listener Started')
        sniff(prn=self.arp_detect, filter="arp", store=0)
