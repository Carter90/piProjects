#! /usr/bin/env python

from scapy.all import * 
    #sudo apt-get install python-scapy
    #sudo -H pip install scapy-python3 --user

print(sys.version_info[0])
if sys.version_info[0] >= 3:
    python3 = True
    import configparser #3
    config = configparser.ConfigParser() #3
else: 
    python3 = False
    import ConfigParser #2
    config = ConfigParser.ConfigParser() #2
config.read('macAddress.conf')

cheezit = 	config.get('Buttons','cheezit')
goldfish =	config.get('Buttons','goldfish')
gaderiad = 	config.get('Buttons','gatorade')

def arp_detect(pkt):
		if pkt.haslayer(ARP) and pkt[ARP].op == 1: #network request
			if pkt[ARP].hwsrc == cheezit:
				print("cheezit")
			if pkt[ARP].hwsrc == goldfish:
				print("goldfish")
			if pkt[ARP].hwsrc == gaderiad:
				print("gatorade")

sniff(prn=arp_detect, filter="arp", store=0)

