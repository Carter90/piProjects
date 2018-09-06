#Some of the TCP/IP Client and Server code from https://pymotw.com/2/socket/tcp.html
def sendMessage(message,retrys=3):
	import socket
	import sys
	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect the socket to the port where the server is listening
	server_address = ('localhost', 19090) #CartersGander #192.168.1.234
	sock.connect(server_address)

	try:
		# Send data
		sock.sendall(message)
		# Look for the response
		amount_received = 0
		amount_expected = len(message)
		received = ""
		while amount_received < amount_expected:
			data = sock.recv(16)
			amount_received += len(data)
			received += data
			print >>sys.stderr, 'received "%s"' % data
		if (received == message):
			print("Message Received")
		else: 
			if retrys > 1:
				print("Message Corrupted Resending")
				sock.close()
				sendMessage(message,retrys-1)
			else:
				print("Message Send Failed")
	finally:
		sock.close()
	sock.close() #just in case

sendMessage("off fans")
#sendMessage("is")
#sendMessage("that")
#sendMessage("the quick brown fox jumps over the lazy dog ")
