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

class RelayControl:
    def __init__(self):
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        self.GPIO = GPIO
        self._pinList = [2, 3, 4, 17, 27, 23, 10, 9]
        self._buttonList = [ 16, 26 ] # TODO: read from server.confg
        # GPIO pins on the Pi so the first relay is at GPIO pin 2, the 4th is at GPIO pin 17
        self._relay_state = [False] * 8
        for index in range(len(self._pinList)):  # turn off all the relays
            print("GPIO.setup pin:" + str(self._pinList[index]))
            GPIO.setup(self._pinList[index], GPIO.OUT)
            GPIO.output(self._pinList[index], GPIO.HIGH)
        for pin in self._buttonList:  # set button pins to 3.3v
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.RISING, callback=self.button_pressed, bouncetime=1500) #was GPIO.FALLING
    
    def _change_relay_state(self, relay_num, new_state):
        print("Setting relay #", relay_num, "to", new_state)
        
        if new_state:
            self.GPIO.output(self._pinList[int(relay_num)-1], self.GPIO.LOW)  # on
            self._relay_state[int(relay_num)-1] = True
        else: 
            self.GPIO.output(self._pinList[int(relay_num)-1], self.GPIO.HIGH)  # off
            self._relay_state[int(relay_num)-1] = False
    
    def invert(self, relay_num):
        print("invert called")
        self._change_relay_state(relay_num, not self.state(relay_num))

    def on(self, relay_num):
        self._change_relay_state(relay_num, True)

    def off(self, relay_num):
        self._change_relay_state(relay_num, False)

    def all_off(self):
        for index in range(len(self._pinList)):
            self._change_relay_state(index+1, False)

    def state(self, relay_num):
        return self._relay_state[int(relay_num)-1]

    def states(self):
        return self._relay_state
        
    def button_pressed(self, channel):
        print("Button Pressed", channel)
        if channel == 26:
            pass #self.invert(8)
        elif channel == 16: #TODO: invistigate why GPIO 16 triggers 26 rising, either coding error or physical wiring 
            pass #self.invert(2)
    
    def __del__(self):
        print("Cleaning up GPIO")
        GPIO.cleanup()

        
class IRControl: # for air conditioner control,
    '''@note had problems with IR on the pi3 b+ works on pi2 b+ have to get that working first'''
    def __init__(self):  
        pass

    def ac_on(self):
        pass

    def ac_off(self):
        pass


class MessageParser:  # TODO: Complete
    def __init__(self, relay_control): 
        self._relay_control = relay_control
        self._validMessage = {'on':self._relay_control.on,
                              'off':self._relay_control.off,
                              'invert':self._relay_control.invert}
        self._relayPattern = re.compile("^([Rr][1-8])$")  # possibility have a range specified in a config
        # TODO: read the config file for fan names and create dictionary to look up corresponding
        # TODO: self._ fan R1 r1 light red [1]
        # TODO: toggle state with other if on and turn on too?
        # TODO: like red: turns off the white light if on and turns r7 on,
        # TODO: line fans: controls both the r2 & r8,

    def decrypt():  # TODO: do maybe refactor to verify too
        pass

    def parse(self, message):
        message = message.split()
        if (self._relayPattern.match(message[1]) is not None) and message[0] in self._validMessage:
            self._validMessage[message[0]](message[1])
        else:  # if (): # TODO: have a look into the dict and if there is a list call multiple relays
            print(message)    
        if message[0] in self._validMessage:
            self._validMessage[message[0]](message[1])


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

class Config:
    def __init__(self):  # TODO: move all the ConfigParser code here
        self.buttons = dict()
        pass

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

