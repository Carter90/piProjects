#! /usr/bin/env python

from scapy.all import * 
	#sudo apt-get install python-scapy
	#sudo -H pip install scapy-python3 --user

class Buttons():
	cheezit, goldfish, gaderiad = "","",""
	#_relay_control = None
	
	def __init__(self, relay_control): 
		self._relay_control = relay_control
		#self._relay_control.invert(2)
		
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

		self.cheezit  = config.get('Buttons','cheezit')
		self.goldfish =	config.get('Buttons','goldfish')
		self.gaderiad = config.get('Buttons','gatorade')

	def arp_detect(self, pkt):
			if pkt.haslayer(ARP) and pkt[ARP].op == 1: #network request
				if pkt[ARP].hwsrc == self.cheezit:
					print("cheezit")
					self._relay_control.invert(2)
					self._relay_control.invert(8)
				if pkt[ARP].hwsrc == self.goldfish:
					print("goldfish")
					self._relay_control.invert(2)
					self._relay_control.invert(8)
				if pkt[ARP].hwsrc == self.gaderiad:
					print("gatorade")
					self._relay_control.invert(2)
					self._relay_control.invert(8)

	def sniffer(self):
		sniff(prn=self.arp_detect, filter="arp", store=0)

