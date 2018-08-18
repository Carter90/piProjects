import socket
import sys, select, os
import signal
import time

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
    _pinList=  [2, 3, 4, 17, 27, 22, 10, 9]
    _relaystate = [False] * 8
    def _change_relay_state(relay_num, new_state):
        print("Setting relay #",relay_num, "to ",new_state)
    #RelayDict or 
    def invert(relayNum):
        _change_relay_state(relayNum, not _relaystate[relayNum-1])
    def on(relayNum):
        _change_relay_state(relayNum, True)
    def off(relayNum):
        _change_relay_state(relayNum, False)
    def state(relayNum):
        return(_relaystate[relayNum-1])
    def states():
        return(_relaystate)

class IRControl:
    pass

class MessageParser:
    pass
       
       
#Some of the TCP/IP Client and Server code from https://pymotw.com/2/socket/tcp.html
if __name__ == '__main__':
	signalCatcher = SignalCatcher() 
	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Bind the socket to the port
	server_address = ('localhost', 19090)
	#print >>sys.stderr, 'starting up on %s port %s' % server_address
	sock.bind(server_address)

	# Listen for incoming connections
	sock.listen(1)
	while signalCatcher.running: # and not (sys.stdin in select.select([sys.stdin], [], [], 0)[0]):
		connection, client_address = sock.accept() # Wait for a connection
		try:
			hasData=True
			while hasData:
				data = connection.recv(16) # Receive the data in small chunks and retransmit it
				if data:
					print data
					connection.sendall(data)
				else:
					hasData = False
		except:
			print("Something Bad Happend")
			connection.close()  # Clean up the connection
			sys.exit(5)
	connection.close()
	print("Exiting")
