import logging
import socket

class clientSocket:

	def __init__(self, sock=None):
		if sock is None:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		else:
			self.sock = sock


	def connect(self, host, port):
		self.sock.connect((host, port))


	def disconnect(self):
		self.send(0)


	def send(self, message):
		totalSent = 0
		message = str(message).encode()
		while totalSent < len(message):
			totalSent = self.sock.send(message[totalSent:])


	def acknowledge(self):
		self.sock.recv(1)
	

	def sendColor(self, color):
		self.send(1)
		# self.acknowledge()
		for var in color:
			var = self.ensureSize(var, 255, 3)
			self.send(var)
			# self.acknowledge()


	def sendBrightness(self, brightness):
		self.send(2)
		brightness = self.ensureSize(brightness, 255, 3)
		self.send(brightness)


	def ensureSize(self, message, maximum, length):
		message = str(message)
		if float(message) > maximum:
			message = str(maximum)
		while len(message) < length:
			message = '0' + message
		return message


	def getColor(self):
		self.send(3)
		h = self.sock.recv(3)
		s = self.sock.recv(3)
		v = self.sock.recv(3)
		return (h, v, s)

	def getBrightness(self):
		self.send(4)
		return self.sock.recv(3)

	def sendRandom(self, times, time):
		self.send(5)
		length = len(times)
		length = self.ensureSize(length, 99, 2)
		self.send(length)
		self.send(times)
		length = len(time)
		length = self.ensureSize(length, 99, 2)
		self.send(length)
		self.send(time)

	def sendPixel(self, pixel, color):
		self.send(6)
		pixel = self.ensureSize(pixel, 299, 3)
		self.send(pixel)
		for var in color:
			var = self.ensureSize(var, 255, 3)
			self.send(var)