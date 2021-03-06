# this is a modified version of an Adafruit example from https://github.com/adafruit/io-client-python/blob/master/examples/mqtt_client.py
# modified by Jordan Faas-Bush


# Example of using the MQTT client class to subscribe to and publish feed values.
# Author: Tony DiCola

# Import standard python modules.
import sys
import time

import clientSocketNEW as clientSocket
import configs as configs

# Import Adafruit IO MQTT client.
from Adafruit_IO import MQTTClient


# Set to your Adafruit IO key & username below.
ADAFRUIT_IO_KEY      = configs.adafruit["key"]
ADAFRUIT_IO_USERNAME = configs.adafruit["username"]  # See https://accounts.adafruit.com
                                                    # to find your username.
FEEDNAME = configs.adafruit["feedname"]

# these are loaded from the config file
IP = configs.server["ip"]
PORT = configs.server["port"]
USER = configs.login["user"]
TOKEN = configs.login["token"]


# this is code just taken from Tristan to connect to the server
def connectToLights(client):
    # logging.debug("Connecting...")
    client.connect(IP, PORT)
    # logging.debug("Authenticating...")
    client.authenticate(USER, TOKEN)
    # logging.debug("Verifying...")
    client.verifyConnected()
    # logging.info("Connected to server")
    return

lightSocket = clientSocket.ClientSocket()
connectToLights(lightSocket)
#lightSocket.send({"mode":"brightness", "brightness":0})

# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening for feed changes...')
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe(FEEDNAME)

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    words = payload.split(" ")
    if len(words) == 1:
        if (payload.lower() == "on"):
            # turn the lights on
            lightSocket.send({"mode":"brightness", "brightness":255})
        elif (payload.lower() == "off"):
            # turn the lights off
            lightSocket.send({"mode":"brightness", "brightness":0})
        elif (payload.lower() == "flash"):
            # this is just for testing
            lightSocket.send({"mode":"brightness", "brightness":0})
            lightSocket.send({"mode":"brightness", "brightness":255})
            lightSocket.send({"mode":"brightness", "brightness":0})
    elif len(words) == 2:
        if (words[0].lower() == "brightnessvalue"):
            value = tryConvertToInt(words[1])
            lightSocket.send({"mode":"brightness", "brightness":value})
        elif (words[0].lower() == "brightnesspercent"):
            percent = tryConvertToFloat(words[1], 0, 0, 100)
            value = int(percent*255/100)
            lightSocket.send({"mode":"brightness", "brightness":value})
        elif (words[0].lower() == "color"):
            # then have a bunch of presets I guess
            colors = {"red":(0, 255, 255), "green":(96, 255, 255), "blue":(164, 255, 255), "purple":(196, 255, 255), "white":(0, 0, 255), "yellow":(54, 255, 255), "pink":(225, 255, 255), "teal":(126, 255, 255), "orange":(23, 213, 255)}
            if (words[1].lower() in colors):
                sendColor(lightSocket, *colors[words[1].lower()])
        elif (words[0].lower() == "colorvalue"):
            hue = tryConvertToInt(words[1])
            sendColor(lightSocket, hue)
    elif len(words) == 4:
        if (words[0].lower() == "colorful"):
            h = tryConvertToInt(words[1])
            s = tryConvertToInt(words[2])
            v = tryConvertToInt(words[3])
            sendColor(lightSocket, h, s, v)
    print('Feed {0} received new value: {1}'.format(feed_id, payload))

def sendColor(client, h = 0, s = 255, v = 255):
    color = {"h":h, "s":s, "v":v}
    client.send({"mode":"solidcolor", "color":color})


def tryConvertToInt(string, defaultValue = 0, minVal = 0, maxVal = 255):
    try:
        val = int(string)
        return max(minVal, min(maxVal, val))
    except ValueError:
        return defaultValue

def tryConvertToFloat(string, defaultValue = 0, minVal = 0, maxVal = 255):
    try:
        val = float(string)
        return max(minVal, min(maxVal, val))
    except ValueError:
        return defaultValue

# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

# Connect to the Adafruit IO server.
client.connect()

# Now the program needs to use a client loop function to ensure messages are
# sent and received.  There are a few options for driving the message loop,
# depending on what your program needs to do.

# The first option is to run a thread in the background so you can continue
# doing things in your program.
"""
client.loop_background()
# Now send new values every 10 seconds.
print('Publishing a new message every 10 seconds (press Ctrl-C to quit)...')
while True:
    value = random.randint(0, 100)
    print('Publishing {0} to DemoFeed.'.format(value))
    client.publish('DemoFeed', value)
    time.sleep(10)
"""

# Another option is to pump the message loop yourself by periodically calling
# the client loop function.  Notice how the loop below changes to call loop
# continuously while still sending a new message every 10 seconds.  This is a
# good option if you don't want to or can't have a thread pumping the message
# loop in the background.
#last = 0
#print('Publishing a new message every 10 seconds (press Ctrl-C to quit)...')
#while True:
#   # Explicitly pump the message loop.
#   client.loop()
#   # Send a new message every 10 seconds.
#   if (time.time() - last) >= 10.0:
#       value = random.randint(0, 100)
#       print('Publishing {0} to DemoFeed.'.format(value))
#       client.publish('DemoFeed', value)
#       last = time.time()

# The last option is to just call loop_blocking.  This will run a message loop
# forever, so your program will not get past the loop_blocking call.  This is
# good for simple programs which only listen to events.  For more complex programs
# you probably need to have a background thread loop or explicit message loop like
# the two previous examples above.
client.loop_blocking() # keep watch forever
