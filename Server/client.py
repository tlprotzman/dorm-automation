import hashlib
import logging
import socket

import configs

class client:

    def __init__(self):
        host = configs.server["ip"]
        port = configs.server["port"]
        logging.info("Connecting to server at " + str(host) + " on port " + str(port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        logging.info("Connection made, authenticating...")


    def authenticate(self, client):
        user = configs.login["user"]
        token = configs.login["token"]
        logging.debug("Authenticating with user " + str(user))
        hasher = hashlib.sha256()
        hasher.update(token.encode())
        hashedToken = hasher.hexdigest()
        auth = {"mode" : "authenticate", 
                "user" : user, "token" : hashedToken}
        self.send(auth)
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