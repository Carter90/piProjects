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

def process(config):
    global signal_catcher
    # TODO: check if config file exists
    signal_catcher = SignalCatcher()                     # calls init
    relay_control = RelayControl()                        # calls init
    dropbox_listener = DropboxListener(relay_control)     # calls init
    dropbox_listener._relay_control = relay_control     # TODO: test if necessary
    local_server = LocalServer(relay_control)
    buttons = Buttons(relay_control)
    buttons._relay_control = relay_control  # TODO: test if necessary

    # Dropbox File Change Listener
    dropbox__thread = Thread(target = dropbox_listener.run)
    
    # Dash Button Listener
    dash_thread = Thread(target = buttons.sniffer)
    
    local_server_thread = Thread(target = local_server.run)
    
    dropbox__thread.start()
    dash_thread.start()  # starts the arp packet sniffer looking for the dash button presses
    local_server_thread.start()
    time.sleep(5)
    if dropbox__thread.isAlive() and dash_thread.isAlive() and local_server_thread.isAlive():
        print('All Threads Started')
    else:
        print("Dropbox Started:",dropbox__thread.isAlive())
        print("Dash Started:",dash_thread.isAlive())
        print("Local Server Started:",local_server_thread.isAlive())
    while signal_catcher.running: 
        time.sleep(2)  # so termination is not immediate
        pass  # keep running until receve kill signal
    #connection.close()        # not sure if I have scope as this is the local server's
    dash_thread.join()         # close the Dash Button thread
    dropbox__thread.join()     # close the Dropbox thread
    local_server_thread.join()     # close the local server thread

if __name__ == '__main__':
    process('/home/carter/relay/PySockets/server.confg')
    print("Main Exiting")
