import logging
import random
import serial
import threading
import time

import configs


# Holds the servers representation of the light strip,
# including its current state, and functions to update
# it.  In theory, should never differ from the physical
# state of the light strip.  In theory.
class lightStrip(): #1000000

    def __init__(self):
        logging.info("Creating the light strip object...")
        # Opens serial port for communication with arduino
        self.uno = serial.Serial(configs.arduino, configs.baud)

        # States about the lights
        self.brightness = 0     # Initializes brightness to 0 on server start
        self.numberOfLEDs = 300 # How many LEDs are on the strip
        self.leds = list()      # Holds each LEDs current color
        for led in range(self.numberOfLEDs):
            self.leds.append((0, 0, 0)) # Initializes color of each LED to (0, 0, 0)

        # Thread locks to allow asynchronous control
        self.colorLock = threading.Lock()
        self.brightnessLock = threading.Lock()
        self.transmitLock = threading.Lock()
        logging.info("Creation complete")

 # Sends a solid color to the strip
    def sendSolidColor(self, color=None):
        logging.info("Sending a solid color to the strip")
        logging.debug("Acquiring color lock")
        self.colorLock.acquire()
        if color is None:   # Checks if a color is specified
            logging.info("Using Current Color")
            if self.verifySolid():  # Ensures the whole strip is actually monochromatic
                color = self.leds[0]
            else:   # Aborts if it is not
                logging.error("Colors are not all same, aborting...")
                return
        else:
            logging.info("Using specified color")
            for i in range(self.numberOfLEDs):
                self.leds[i] = color
        logging.debug("Color is " + str(color)) # Color to use is now known
        logging.info("Sending color")
        logging.debug("Acquiring transmit lock")
        self.transmitLock.acquire()     # Prepares to send the command to the arduino
        self.uno.write(b"SETCOLOR~")    # Tells the arduino to expect a color
        for value in color:     # Converts each value in the color to a 'command'
            if not int(value) in range(256):
                logging.warning("Color value out of range, changed to 0")
                value = 0
            command = str(value) + '~'
            logging.debug("Sending command: " + command)
            self.uno.write(command.encode())    # Sends the command to the arduino
        self.transmitLock.release()
        logging.debug("Released transmit lock")
        self.colorLock.release()
        logging.debug("Released color lock")

    # Sends the currently set brightness to the arduino
    def sendBrightness(self):
        logging.info("Sending brightness value " + str(self.brightness))
        logging.debug("Acquiring brightness lock")
        self.brightnessLock.acquire()
        logging.debug("Acquiring transmit lock")
        self.transmitLock.acquire()
        logging.info("Sending brightness...")
        self.uno.write(b"SETBRIGHTNESS~")       # Tells arduino to expect a brightness
        command = str(self.brightness) + '~'    # Converts the brightness to command form
        self.uno.write(command.encode())        # Sends brightness to arduino
        self.transmitLock.release()
        logging.debug("Released transmit lock")
        self.brightnessLock.release()
        logging.debug("Released brightness lock")
        logging.info("Brightness sent")


    # Gets the current color
    def getColor(self):
        logging.debug("Current color is " + str(self.leds[0]))
        return self.leds[0]


    # Gets the current brightness
    def getBrightness(self):
        logging.debug("Current brightness is " + str(self.brightness))
        return self.brightness


    # Prompts for input from the user, and sets and sends the brightness
    def setBrightness(self, brightness, send=True):
        logging.debug('Acquire brightness lock')
        self.brightnessLock.acquire()
        self.brightness = brightness
        self.brightnessLock.release()
        logging.debug('Release brightness lock')
        if send:
            self.sendBrightness()


    # Sets the current color of the entire strip
    def setColor(self, color, send=True):
        if send:
            self.sendSolidColor(color)
        else:
            logging.debug("Acquiring color lock")
            self.colorLock.acquire()
            for i in range(self.numberOfLEDs):
                self.leds[i] = color
            self.colorLock.release()
            logging.debug("Released color lock")


    # Sets and shows an individual pixel
    def setPixel(self, pixel, color):
        pass
        # logging.debug('Acquire color lock')
        # self.colorLock.acquire()
        # logging.debug('Acquire transmit lock')
        # self.transmitLock.acquire()
        # self.uno.write(b'SETPIXELSHOW~')
        # command = str(pixel) + '~'
        # self.uno.write(command.encode())
        # for var in color:
        #     command = str(var) + '~'
        #     logging.debug("Sending command: " + command)
        #     self.uno.write(str.encode(command))
        # self.transmitLock.release()
        # logging.debug('Release transmit lock')
        # self.colorLock.release()
        # logging.debug('Release color lock')



    def sendStrand(self, colors):
        pass
        # logging.debug("Setting strand")
        # self.uno.write(b"SETSTRIP~")
        # for pixel in colors.keys():
        #     logging.debug("Setting pixel " + str(pixel) + " to " + str(colors[pixel]))
        #     command = str(pixel) + '~'
        #     while self.uno.out_waiting:
        #         pass
        #     self.uno.write(command.encode())
        #     value = ''
        #     for color in colors[pixel]:
        #         value = str(color) + '~'
        #         while self.uno.out_waiting:
        #             pass
        #         self.uno.write(value.encode())
        # logging.debug("Showing changes...")
        # while self.uno.out_waiting:
        #     pass
        # self.uno.write(b"SHOW~")
        # while self.uno.inWaiting():
        #     print(self.uno.readline().strip())
        # # for line in self.uno.readlines():
        # #   logging.debug("SERIAL RETURN MESSAGES: "+str(line))


    # Fades the lights up from 0
    def fadeUp(self):
        pass
        # logging.debug('Acquire brightness lock')
        # self.brightnessLock.acquire()
        # i = 1   
        # while i < 255:
        #     self.brightness = i
        #     self.sendBrightness()
        #     time.sleep(0.1)
        #     i += i * 1.05
        # self.brightnessLock.release()
        # logging.debug('Release brightness lock')


    # Fades the lights down to 0
    def fadeDown(self):
        pass
        # logging.debug('Acquire brightness lock')
        # self.brightnessLock.acquire()
        # while self.brightness > 0:
        #     self.brightness -= 1
        #     self.sendBrightness()
        #     time.sleep(0.1)
        # self.brightnessLock.release()
        # logging.debug('Release brightness lock')


    # Controls the above fade functions
    def fade(self):
        pass
        # direction = input("Fade up or down? ")
        # if direction.lower() == "up":
        #     self.fadeUp()
        # elif direction.lower() == "down":
        #     self.fadeDown()


    # Makes the lights flash random colors at a specified rate
    def randomColor(self, iterations, delay):
        pass
        # logging.debug('Acquire color lock')
        # self.colorLock.acquire()
        # for i in range(iterations):
        #     values = list()
        #     for j in range(3):
        #         values.append(random.randint(0, 255))
        #     self.color = (values[0], values[1], values[2])
        #     self.sendColor()
        #     time.sleep(delay)
        # self.colorLock.release()
        # logging.debug('Release color lock')


    def rainbow(self, iterations, delay):
        pass
        # for i in range(iterations):
        #     for color in range(255):
        #         self.setColor((color, 255, 255))
        #         time.sleep(delay)


    # Checks if all the lights are the same color
    def verifySolid(self):
        color = self.leds[0]
        for led in self.leds:
            if led != color:
                return False
        return True