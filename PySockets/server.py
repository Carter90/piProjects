from __future__ import print_function
from scapy.all import * 
	#sudo apt-get install python-scapy
	#sudo -H pip install scapy-python3 --user
import socket
import sys, select, os
import signal
import time
from threading import Thread
import re
import RPi.GPIO as GPIO
import urllib2
import datetime


#https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
#Thanks to Mayank Jaiswal for help with signal handleing 
class SignalCatcher:
	running = True
	def __init__(self):
		signal.signal(signal.SIGINT, self.exit_called)
		signal.signal(signal.SIGTERM, self.exit_called)

	def exit_called(self,signum, frame):
		self.running = False
		try:
			connection.close() # Clean up the connection
			print("Cleaning up ... Exiting")
		except NameError:
			print("No prior connections made ... Exiting")
		sys.exit(1)

class RelayControl:
	def __init__(self):
		import RPi.GPIO as GPIO
		GPIO.setmode(GPIO.BCM)
		self.GPIO = GPIO
		self._pinList =  [2, 3, 4, 17, 27, 22, 10, 9]
		self._relaystate = [False] * 8
		for index in range(len(self._pinList)):
			GPIO.setup(self._pinList[index], GPIO.OUT)
			GPIO.output(self._pinList[index], GPIO.HIGH)
	def _change_relay_state(self,relay_num, new_state):
		print("Setting relay #",relay_num, "to",new_state)
		
		if (new_state):
			self.GPIO.output(self._pinList[int(relay_num)-1], self.GPIO.LOW)
			self._relaystate[int(relay_num)-1] = True
		else: 
			self.GPIO.output(self._pinList[int(relay_num)-1], self.GPIO.HIGH)
			self._relaystate[int(relay_num)-1] = False
		
	#RelayDict or 
	def invert(self,relayNum):
		print("invert called")
		self._change_relay_state(relayNum, not self._relaystate[relayNum-1])
	def on(self,relayNum):
		self._change_relay_state(relayNum, True)
	def off(self,relayNum):
		self._change_relay_state(relayNum, False)
	def all_off():
		for index in range(len(self._pinList)):
			self._change_relay_state(index+1, False)
	def state(self,relay_num):
		return(self._relaystate[int(relay_num)-1])
	def states(self):
		return(self._relaystate)

	def __del__(self):
		print("Cleaning up GPIO")
		#GPIO.cleanup()
		
class IRControl:
	pass

class MessageParser:
	def __init__(self, relay_control): 
		self._relay_control = relay_control
		self._validMessage = {'on':self._relay_control.on,'off':self._relay_control.off,'invert':self._relay_control.invert}
		self._relayPattern = re.compile("^([Rr][1-8])$")
		#self._ fan R1 r1 light red [1]
		#toggle state with other if on and turn on too?
		#red: turns off the white light if on and turns r7 on, fans: controlls both the r2 & r8, 

	def parse(self, message):
		message = message.split()
		if (self._relayPattern.match("R2") is not None) and message[0] in self._validMessage:
			self._validMessage[message[0]](message[1])
		else: #if ():
			print(message)	
		if message[0] in self._validMessage:
			self._validMessage[message[0]](message[1])

class DropboxListener:
	def __init__(self, relay_control): 
		self._relay_control = relay_control
		self.page_url = 'https://carter.page.link/relayState'
		self.page = []
		self._updated_page = urllib2.urlopen(urllib2.Request(self.page_url)).read().replace('\r', '').split('\n')
	def run(self):	 
		try:
			while self._updated_page[8] != 'stop': #if I have to remotly kill it
				if (self.page != self._updated_page):
					self.page = self._updated_page
					print('Dropbox update:',datetime.datetime.now())
					for index in range(8):
						if self.page[index] == 'T':
							self._relay_control.on(index+1)
						else: 
							self._relay_control.off(index+1)
						time.sleep(.01)
					print('-------------------------')
				time.sleep(.1)
				self._updated_page = urllib2.urlopen(urllib2.Request(self.page_url)).read().replace('\r', '').split('\n')
			print('Dropbox Stop Code Receved')
		except Exception, e:
			print("Something borked stopping",str(e))
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
		config.read('/home/carter/relay/PySockets/macAddress.conf')

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
		print('Dash Button Listener Started')
		sniff(prn=self.arp_detect, filter="arp", store=0)

#Some of the TCP/IP Client and Server code from https://pymotw.com/2/socket/tcp.html
class LocalServer:
	def __init__(self, relay_control): 
		# Create a TCP/IP socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Bind the socket to the port
		server_address = ('', 19090)
		self.sock.bind(server_address)
	
		# Listen for incoming connections
		self.sock.listen(1)
		
		self._relay_control = relay_control
		message_parser = MessageParser(relay_control)
		#message_parser.parse("on r1") #just testing
		#message_parser.parse("true r2")
		#message_parser.parse("off fans")
		
	def run(self):
		while signal_catcher.running: # and not (sys.stdin in select.select([sys.stdin], [], [], 0)[0]):
			connection, client_address = self.sock.accept() # Wait for a connection
			try:
				hasData=True
				while hasData:
					data = connection.recv(16) # Receive the data in small chunks and retransmit it
					if data:
						print(data)
						message_parser(data) #thinking of concatinating data before sending to parser
						connection.sendall(data)
					else:
						hasData = False
			except:
				print("Something Bad Happend")
				connection.close()  # Clean up the connection
		connection.close()

if __name__ == '__main__':
	signal_catcher = SignalCatcher() 	#calls init
	relay_control = RelayControl()		#calls init
	dropbox_listener = DropboxListener(relay_control)#calls init
	dropbox_listener._relay_control = relay_control
	local_server = LocalServer(relay_control)
	buttons = Buttons(relay_control)
	buttons._relay_control = relay_control

	#Dropbox File Change Listener
	dropbox__thread = Thread(target = dropbox_listener.run)
	
	#Dash Button Listener
	dash_thread = Thread(target = buttons.sniffer)
	
	local_server_thread = Thread(target = local_server.run)
	
	dropbox__thread.start()
	dash_thread.start() #starts the arp packet sniffer looking for the dash button presses
	local_server_thread.start()
	
	print('All Started')
	#if (dropbox__thread.isAlive())
	runme = True
	while runme: #signal_catcher.running: # and not (sys.stdin in select.select([sys.stdin], [], [], 0)[0]):
		runme = bool(input()) #need to return sooner
		'''except:
			print("Something Bad Happend")
			connection.close()  # Clean up the connection
			sys.exit(5)'''
	connection.close()
	dash_thread.join() 		#close the Dash Button thread
	dropbox__thread.join() 	#close the Dropbox thread
	print("Exiting")
	
