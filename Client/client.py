#! /usr/bin/python3
import hashlib
import logging
import random
import serial
import sys
import time

import configs
import clientSocket

# ip = "localhost"
ip = configs.server['ip']
port = configs.server["port"]
token = configs.login["token"]

def main():
	logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
	client = clientSocket.clientSocket()
	authenticate(client)
	while True:
		command = input("Enter a command: ")
		command = command.strip().lower()
		if command == "color-full":
			color(client)
		if command == "color":
			color(client, hue=True)
		elif command == "brightness":
			brightness(client)
		elif command == "get brightness":
			print(client.getBrightness())
		elif command == "get color":
			print(client.getColor())
		elif command == "random":
			random(client)
		elif command == "exit":
			client.disconnect()
			sys.exit()
		elif command == "pixel":
			pixel(client)
		elif command == "rainbow":
			rainbow(client)
		elif command == "pulse":
			speed = float(input("How fast? (delay between steps) "))
			h = input("Enter a H value: ")
			s = input("Enter a S value: ")
			v = input("Enter a V value: ")
			for i in range(300):
				client.sendPixel(i, (h, s, v))
				time.sleep(speed)
		elif command == "striptest":
			randomColors(client)
		elif command == "color-fade":
			colorFade(client)
		elif command == "brightness-fade":
			brightnessFade(client)
		elif command == "off":
			off(client)



def authenticate(client):
	client.connect(ip, port)
	hasher = hashlib.sha256()
	hasher.update(token.encode())
	hashed = hasher.hexdigest()
	client.send(hashed)
	client.verifyConnected()

def color(client, hue=False):
	h = input("Enter a H value: ")
	s = 255
	v = 255
	if not hue:
		s = input("Enter a S value: ")
		v = input("Enter a V value: ")
	client.sendColor((h, s, v))


def brightness(client):
	brightness = input("Enter brightness: ")
	client.sendBrightness(brightness)


def random(client):
	times = input("How many iterations should it run? ")
	delay = input("How long should it delay? ")
	client.sendRandom(times, delay)


def pixel(client):
	pixel = input("Which pixel? ")
	h = input("Enter a H value: ")
	s = input("Enter a S value: ")
	v = input("Enter a V value: ")
	client.sendPixel(pixel, (h, s, v))


def rainbow(client):
	for j in range(5):
		for i in range(255):
			client.sendColor((i, 255, 255))
			time.sleep(0.05)

def randomColors(client):
	client.sendRandomStrip()

def colorFade(client):
	color = input("Enter H value: ")
	currentColor = int(client.getColor()[0])
	while int(currentColor) != int(color):
		currentColor = (currentColor + 1) % 255
		client.sendColor((currentColor, 255, 255))
		time.sleep(0.03)

def brightnessFade(client):
	brightness = input("Enter target brightness: ")
	currentBrightness = int(client.getBrightness())
	while currentBrightness < int(brightness):
		currentBrightness += 1
		client.sendBrightness(currentBrightness)
		time.sleep(0.03)
	while currentBrightness > int(brightness):
		currentBrightness -= 1
		client.sendBrightness(currentBrightness)
		time.sleep(0.03)

def off(client):
	currentBrightness = int(client.getBrightness())
	while currentBrightness:
		currentBrightness -= 1
		client.sendBrightness(currentBrightness)
		time.sleep(0.03)


if __name__ == "__main__":
	main()
