import hashlib
import json
import logging
import socket
import sys

class ClientSocket:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return

    def connect(self, host, port):
        logging.info("Connecting to server at " + str(host) + " on port " + str(port))
        self.sock.connect((host, port))
        return

    def disconnect(self):
        self.send({"mode" : "disconnect"})
        self.sock.close()
        

    def authenticate(self, user, token):
        logging.info("Attempting to authenticate")
        hasher = hashlib.sha256()
        hasher.update(token.encode())
        hashedToken = hasher.hexdigest()
        auth = {"user" : user, "token" : hashedToken}
        self.send(auth)
        return

    def verifyConnected(self):
        connected = self.sock.recv(1).decode()
        if connected:
            logging.info("Successfully connected!")
        else:
            logging.critical("Failed to connect. Exiting...")
            self.sock.close()
            sys.exit(1)
        return

    def send(self, obj):
        payload = json.dumps(obj)
        size = len(payload)
        logging.info("Sending message of size " + str(size))
        logging.debug("Sending " + payload)
        size = self.ensureSize(size, 9999, 4)
        self._send(size)
        self._send(payload)
        return


    def _send(self, message):
        totalSent = 0
        message = str(message).encode()
        while totalSent < len(message):
            totalSent += self.sock.send(message[totalSent:])
            logging.debug("Sent " + str(totalSent) + " of " + str(len(message)) + "bytes")
        return

    def receive(self):
        logging.debug("Waiting to receive message")
        size = self.sock.recv(4)
        logging.debug("Receiving message of size " + str(size))
        data = self.sock.recv(int(size))
        logging.debug("Received " + data)
        obj = json.loads(data)
        logging.info("Received message from server")
        return obj

    def ensureSize(self, message, maximum, length):
        message = str(message)
        if float(message) > maximum:
            logging.critical("ERROR: Value larger than maximum size. Behavior may not be defined")
            message = str(maximum)
        if len(message) >= length:
            message = message[:length]
        while len(message) < length:
            message = '0' + message
        return message