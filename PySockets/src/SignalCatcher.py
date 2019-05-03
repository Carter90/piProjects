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

# https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
# Thanks to Mayank Jaiswal for help with signal handling
class SignalCatcher:
    def __init__(self):  # TODO: pass and instance of a main class that holds all the things to clean up
        self.running = True
        signal.signal(signal.SIGINT, self.exit_called)  # Ctrl+C
        signal.signal(signal.SIGTERM, self.exit_called)  # Termination signal #15

    def exit_called(self, signum, frame):
        global connection
        try:
            print("Got signal:", signum, " from", frame)
            connection.close()  # Clean up the connection, possible scope problem
            sock.close()  # Local Listener
            print("Cleaning up ... Exiting")
        except NameError:
            print("No prior connections made ... Exiting")
        self.running = False  # exit case for loops
    
    def __del__(self):
        pass

