#! /usr/bin/env python

from scapy.all import *
from lifxlan import *
#import configparser #3
import ConfigParser #2
#config = configparser.ConfigParser() #3
config = ConfigParser.ConfigParser()
config.read('macAddress.conf')

cheezit = 	config.get('Buttons','cheezit')
goldfish =	config.get('Buttons','goldfish')
gaderiad = 	config.get('Buttons','gaderiad')


def arp_detect(pkt):
		if pkt[ARP].op == 1: #network request
			if pkt[ARP].hwsrc == cheezit:
				print("cheezit")
			if pkt[ARP].hwsrc == goldfish:
				print("goldfish")
			if pkt[ARP].hwsrc == gaderiad:
				print("gaderiad")

sniff(prn=arp_detect, filter="arp", store=0)

