#! /usr/bin/python3
import logging
import socket
import sys
import threading
import time

import configs

def main(args):
    server = init(level=logging.DEBUG, attempts=10)

def parseArgs(args):
    pass

def init(level=logging.INFO, attempts=1):
    # Initializes logging
    logging.basicConfig(level=level, format='%(relativeCreated)6d %(threadName)s %(message)s')
    logging.info("Logging started at level " + str(level))


    # Starts the server
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.info("Starting server")
    if attempts > 0:
        for i in range(attempts):
            if start(serverSocket, i, attempts):
                break
    else:
        i = 0
        while not start(serverSocket, i, attempts):
            i += 1
    logging.info("Started server at " + configs.server["ip"] + " on port " + str(configs.server["port"]))
    return serverSocket



def start(serverSocket, i, attempts):
    # Attempts to open a socket on the requested location and port
    ip = configs.server["ip"]
    port = configs.server["port"]
    try:
        serverSocket.bind((ip, port))
        return True
    except:
        if i == 0:
            logging.error("Error: Unable to start server at " + ip + " on port " + str(port))
            logging.error("Perhaps the server did not go down cleanly and the port hasn't been released?")
        elif i == attempts - 1:
            logging.critical("Exiting...")
            sys.exit(1)
        logging.error("Trying again...")
        time.sleep(1)
        return False
    # Success! 

def listen()

if __name__ == '__main__':
    main(sys.argv)