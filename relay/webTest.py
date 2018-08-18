#!/usr/bin/python
from __future__ import print_function
import RPi.GPIO as GPIO
import time
import urllib2
import datetime
GPIO.setmode(GPIO.BCM)
page_url = 'https://carter.page.link/relayState'

# init list with pin numbers
pinList = [2, 3, 4, 17, 27, 22, 10, 9]
page = []

for index in range(len(pinList)):
	GPIO.setup(pinList[index], GPIO.OUT) 
	GPIO.output(pinList[index], GPIO.HIGH)

try:
	updated_page = urllib2.urlopen(urllib2.Request(page_url)).read().split('\n')
	
	while updated_page[8] != 'stop': #if I have to remotly kill it
		if (page != updated_page):
			page = updated_page
			print(datetime.datetime.now())
			for index in range(len(pinList)):
				print("Relay:",index,"\tSet to:",page[index])
				if page[index] == 'T':
					GPIO.output(pinList[index], GPIO.LOW)
				else: 
					GPIO.output(pinList[index], GPIO.HIGH)
				time.sleep(.01)
			print('-------------------------')
		time.sleep(.1)
		updated_page = urllib2.urlopen(urllib2.Request(page_url)).read().split('\n')
except Exception, e:
	print("Something borked stopping",str(e))
	GPIO.cleanup()

print("Exited via remote stop signal")
GPIO.cleanup()
