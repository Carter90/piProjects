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

#Some of the TCP/IP Client and Server code from https://pymotw.com/2/socket/tcp.html
class LocalServer:
    message_parser = None
    def __init__(self, relay_control):
        global sock
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind the socket to the port
        server_address = ('', 19090)  # '' will use localhost, port #
        self.sock.bind(server_address)
    
        # Listen for incoming connections
        self.sock.listen(1)
        
        self._relay_control = relay_control
        message_parser = MessageParser(relay_control)
        ''' #testing
        message_parser.parse("on r1")
        message_parser.parse("true r2")
        message_parser.parse("off fans")
        ''' #end testing
        self.sock.close()  # what? ****************************************************************************************
        
    def run(self):
        global signal_catcher
        global connection
        while signal_catcher.running:  # and not (sys.stdin in select.select([sys.stdin], [], [], 0)[0]):
            connection, client_address = self.sock.accept()  # Wait for a connection
            try:
                has_data=True
                while has_data:
                    data = connection.recv(16)  # Receives the data in small chunks and retransmit it
                    if data:
                        print("Local Server Data Received:", data)
                        message_parser.parse(data)  # TODO: concatenate data before sending to parser
                        connection.sendall(data)  # TODO: only if successful send reply for security
                    else:
                        has_data = False
            except:
                print("Something Bad Happened")
                connection.close()  # Clean up the connection
        connection.close()
