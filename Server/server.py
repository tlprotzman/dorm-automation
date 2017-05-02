#! /usr/bin/python3
import logging
import socket
import sys
import threading
import time

import configs
import lightStrip

ip = configs.server["ip"]
port = configs.server["port"]

def main(args):
	# Creates an instance of the light strip class
	lights = lightStrip.lightStrip()
	# Starts logging
	logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
	logging.debug("Logging started...")

	# Starts the server
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	start(serverSocket)

	# Listens for and processes requests
	listen(serverSocket, lights)

	# Closes the server
	logging.debug("Closing the server...")
	serverSocket.close()

def start(serverSocket):
	# Attempts to open a socket on the requested location and port
	logging.debug("Starting server")
	try:
		serverSocket.bind((ip, port))
	except:
		logging.debug("Error: Unable to start server at " + ip + " on port " + str(port))
		logging.debug("Perhaps the server did not go down cleanly and the port hasn't been released?")
		logging.debug("Exiting...")
		sys.exit(1)
	# Success! 
	logging.debug("Started server at " + ip + " on port " + str(port))

def listen(serverSocket, lights):
	# Listens for up to 5 requests at a time
	serverSocket.listen(5)
	listening = True
	clientThreads = list()
	index = 0
	while listening:
		clientSocket, address = serverSocket.accept()	# Listens for a new connection
		# Attempt to authenticate the user
		if not authenticate(clientSocket):
			continue

		# Spawns a thread to process the users requests
		name = "clientThread-" + str(index)
		index += 1
		t = threading.Thread(name=name, target=clientThread, args=(clientSocket, lights,))
		clientThreads.append(t)
		t.start()


def authenticate(clientSocket):
	logging.debug("New connection made, waiting for authentication...")
	# Sets a short timeout to force quick authentication 
	clientSocket.settimeout(4)
	auth = ''
	try:	# Attempts to receive a 64 bit hash from the client
		auth = clientSocket.recv(64).decode()
	except:
		pass

	clientSocket.settimeout(None)
	# Uses sha256 hash
	if auth != configs.accounts["admin"]:
		logging.debug("Authenticaion failed.  Disconnecting user")
		send(0, clientSocket)	# Sends a 0, indicating a failed authentication
		clientSocket.close()
		return False
	send(1, clientSocket)		# Sends a 1, indication a successful authentication
	logging.debug("Authentication successful!")
	return True


# Sends a message to the client
def send(message, client):
		totalSent = 0	# Tracks how much of the message has been sent
		message = str(message).encode()	# Encodes the message as a utf-8
		while totalSent < len(message):	# Continues sending while the message isn't fully set
			totalSent = client.send(message[totalSent:])	# Sends the remainder of the string


# Handles a single client, processing requests from it
def clientThread(clientSocket, lights):
	"""
	CODES:
	0		Disconnect the client
	1		Receive a color code
	2		Receive a brightness
	3		Request for current color
	4		Request for current brightness
	5		Starts a random sequence
	6		Receives an individual pixel
	"""

	logging.debug("Started client socket thread for " + str(clientSocket))
	# Listens for a request from the client
	while True:
		data = clientSocket.recv(1).decode()		# Receives the code for the desired command
		logging.debug("received: " + str(data))
		if data == "1":
			color = receiveColor(clientSocket)
			processCommands(lights, ("color", color))
		elif data == "2":
			brightness = clientSocket.recv(3).decode()
			logging.debug("Received brightness " + str(brightness))
			processCommands(lights, ("brightness", brightness))
		elif data == "3":
			logging.debug("Request for current color made")
			for var in lights.getColor():
				var = ensureSize(str(var), 255, 3)
				send(var, clientSocket)
		elif data == "4":
			logging.debug("Request for current brightness made")
			send(ensureSize(str(lights.getBrightness()), 255, 3), clientSocket)
		elif data == "5":
			logging.debug("Starting random sequence")
			randomInfo = receiveRandom(clientSocket)
			processCommands(lights, ("random", randomInfo))
		elif data == "6":
			logging.debug("Receiving individual pixel")
			receivePixel(lights, clientSocket)
		elif data == "7":
			logging.debug("Receiving entire strip")
			receiveStrip(lights, clientSocket)
		if not data:
			logging.debug("Closing thread")
			clientSocket.close()
			break


# Receives a color from the client
def receiveColor(clientSocket):
	logging.debug("Receiving color...")
	data = list()
	for i in range(3):	# Receives 3 3 digit numbers
		data.append(clientSocket.recv(3).decode())
	color = (data[0], data[1], data[2])	# Saves the color to a tuple
	logging.debug("Received color " + str(color))
	return color


# Receives the information needed to start a random sequence
def receiveRandom(clientSocket):
	length = int(clientSocket.recv(2))		# Gets the length for number of times
	times = int(clientSocket.recv(length))	# Number of times
	length = int(clientSocket.recv(2))		# Gets the length for delay
	delay = float(clientSocket.recv(length))# Gets the delay	
	logging.debug("Received random with iterations " + str(times) + " and delay " + str(delay))
	return (times, delay)


# Reveives a individual pixel's data
def receivePixel(lights, clientSocket):
	logging.debug("Setting pixel")
	pixel = int(clientSocket.recv(3))	# Gets the pixel
	color = receiveColor(clientSocket)	# Gets the color
	logging.debug("Setting pixel " + str(pixel) + " to color " + str(color))
	lights.setPixel(pixel, color)		# Sets the pixel


# 'Attempts' to set the entire strip individully
def receiveStrip(lights, clientSocket):
	strip = dict()
	numPixles = int(clientSocket.recv(3))
	logging.debug("Receiving " + str(numPixles) + " pixels")
	for i in range(numPixles):
		pixel = int(clientSocket.recv(3))
		logging.debug("received pixel " + str(pixel))
		color = receiveColor(clientSocket)
		strip[pixel] = color
		logging.debug("Pixel " + str(pixel) + " assigned to color " + str(color))
	lights.sendStrand(strip)

def processCommands(lights, commands):
	if not commands:
		logging.debug("ERROR: No command specified")
		return
	elif commands[0] == "color":
		color = (commands[1][0], commands[1][1], commands[1][2])
		lights.setColor(color)
	elif commands[0] == "brightness":
		lights.setBrightness(commands[1])
	elif commands[0] == "random":
		lights.randomColor(commands[1][0], commands[1][1])


def ensureSize(message, maximum, length):
	if int(message) > maximum:
		message = str(maximum)
	if len(message) >= length:
		message = message[:length]
	while len(message) < length:
		message = '0' + message
	return message


if __name__ == "__main__":
	main(sys.argv)

