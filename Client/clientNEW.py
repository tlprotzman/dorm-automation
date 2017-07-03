#! /usr/bin/python3
import logging
import sys
import readline

import configs
import clientSocketNEW as clientSocket

IP = configs.server["ip"]
PORT = configs.server["port"]
USER = configs.login["user"]
TOKEN = configs.login["token"]

def main():
    logging.basicConfig(level=logging.ERROR, format='%(relativeCreated)6d %(threadName)s %(message)s')
    client = clientSocket.ClientSocket()
    connect(client)
    while True:
        command = input("Enter a command: ")
        command = command.strip().lower()
        if command == "color":
            color(client, hue=True)
        elif command == "colorful":
            color(client)
        elif command == "color-fade":
            colorFade(client, hue=True)
        elif command == "colorfuul-fade":
            colorFade(client)
        elif command == "brightness":
            brightness(client)
        elif command == "brightness-fade":
            brightnessFade(client)
        elif command == "pulse":
            pulse(client)
        elif command == "rainbow":
            rainbow(client)
        elif command == "on":
            on(client)
        elif command == "off":
            off(client)
        elif command == "exit":
            client.disconnect()
            sys.exit(0)


def connect(client):
    logging.debug("Connecting...")
    client.connect(IP, PORT)
    logging.debug("Authenticating...")
    client.authenticate(USER, TOKEN)
    logging.debug("Verifying...")
    client.verifyConnected()
    logging.info("Connected to server")
    return

def color(client, hue=False):
    newColor = dict()
    newColor["h"] = numInput("Enter a H value: ", 255)
    newColor["s"] = newColor["v"] = 255
    if not hue:
        newColor["s"] = numInput("Enter a S value: ", 255)
        newColor["v"] = numInput("Enter a V value: ", 255)
    command = {"mode" : "solidColor", "color" : newColor}
    client.send(command)
    return

def colorFade(client):
    newColor = dict()
    newColor["h"] = numInput("Enter a H value: ", 255)
    newColor["s"] = newColor["v"] = 255
    if not hue:
        newColor["s"] = numInput("Enter a S value: ", 255)
        newColor["v"] = numInput("Enter a V value: ", 255)
    fadeTime = numInput("Enter fade time: ")
    command = {"mode" : "solidColor", "color" : newColor,
               "fadeTime" : fadeTime}
    client.send(command)
    return


def brightness(client):
    brightness = numInput("Enter brightness: ", 255)
    command = {"mode" : "brightness", "brightness" : brightness}
    client.send(command)
    return

def brightnessFade(client):
    targetBrightness = numInput("Enter target brightness: ", 255)
    fadeTime = numInput("Enter fade time: ")
    command = {"mode" : "brightnesFfade", "brightness" = targetBrightness,
               "fadeTime" : fadeTime}
    client.send(command)
    return



def numInput(string, maxVal=None):
    while True:
        data = input(string)
        try:
            data = int(data)
            if maxVal is None or data <= maxVal:
                return data
        except:
            print("Invalid number.")


if __name__ == '__main__':
    main()
