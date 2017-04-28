import logging
import random
import serial
import threading
import time

import configs

class lightStrip():

	def __init__(self):
		self.uno = serial.Serial(configs.arduino, 1000000)  # Where to talk to the arduino
		self.brightness = 0		  					# Current brightness
		self.color = (0, 0, 0)						# Current color

		# Locks to allow asynchronous control
		self.colorLock = threading.Lock()
		self.brightnessLock = threading.Lock()
		self.transmitLock = threading.Lock()

	# Sends the currently set color to the arduino
	def sendColor(self, color=None):
		self.transmitLock.acquire()
		logging.debug('Acquire transmit lock')
		self.uno.write(b'SETCOLOR~')
		if color is None:
			color = self.color
		for var in color:
			command = str(var) + '~'
			logging.debug("Sending command: " + command)
			self.uno.write(str.encode(command))
		self.transmitLock.release()
		logging.debug('Release transmit lock')

	# Sends the currently set brightness to the arduino
	def sendBrightness(self):
		self.transmitLock.acquire()
		logging.debug('Acquire transmit lock')
		self.uno.write(b'SETBRIGHTNESS~')
		command = str(self.brightness) + '~'
		self.uno.write(str.encode(command))
		logging.debug("Sending command: " + command)
		self.transmitLock.release()
		logging.debug('Release transmit lock')


	# Gets the current brightness from the arduino
	def getBrightness(self):
		return self.brightness

	def getColor(self):
		return self.color

	# Prompts for input from the user, and sets and sends the brightness
	def setBrightness(self, brightness):
		self.brightnessLock.acquire()
		logging.debug('Acquire brightness lock')
		self.brightness = brightness
		self.sendBrightness()
		self.brightnessLock.release()
		logging.debug('Release brightness lock')

	# Fades the lights up from 0
	def fadeUp(self):
		self.brightnessLock.acquire()
		logging.debug('Acquire brightness lock')
		i = 1	
		while i < 255:
			self.brightness = i
			self.sendBrightness()
			time.sleep(0.1)
			i += i * 1.05
		self.brightnessLock.release()
		logging.debug('Release brightness lock')

	# Fades the lights down to 0
	def fadeDown(self):
		self.brightnessLock.acquire()
		logging.debug('Acquire brightness lock')
		while self.brightness > 0:
			self.brightness -= 1
			self.sendBrightness()
			time.sleep(0.1)
		self.brightnessLock.release()
		logging.debug('Release brightness lock')

	# Controls the above fade functions
	def fade(self):
		direction = input("Fade up or down? ")
		if direction.lower() == "up":
			self.fadeUp()
		elif direction.lower() == "down":
			self.fadeDown()

	# Sends the specified color
	def setColor(self, color):
		self.colorLock.acquire()
		logging.debug('Acquire color lock')
		self.color = color
		self.sendColor()
		self.colorLock.release()
		logging.debug('Release color lock')

	# Makes the lights flash random colors at a specified rate
	def randomColor(self, iterations, delay):
		self.colorLock.acquire()
		logging.debug('Acquire color lock')
		for i in range(iterations):
			values = list()
			for j in range(3):
				values.append(random.randint(0, 255))
			self.color = (values[0], values[1], values[2])
			self.sendColor()
			time.sleep(delay)
		self.colorLock.release()
		logging.debug('Release color lock')

	def setPixel(self, pixel, color):
		self.colorLock.acquire()
		logging.debug('Acquire color lock')
		self.transmitLock.acquire()
		logging.debug('Acquire transmit lock')
		self.uno.write(b'SETPIXEL~')
		command = str(pixel) + '~'
		self.uno.write(command.encode())
		for var in color:
			command = str(var) + '~'
			logging.debug("Sending command: " + command)
			self.uno.write(str.encode(command))
		self.transmitLock.release()
		logging.debug('Release transmit lock')
		self.colorLock.release()
		logging.debug('Release color lock')