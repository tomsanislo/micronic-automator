#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket

class Decapper():

    def __init__(self):

        "basic constructor"

        self.__readBuffer = ""

        self.socket_com = None

        self.__fs = None

        self.__connected = False


    def initialise(self, host, port):

        self.socket_com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:

            self.socket_com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.socket_com.connect((host, port))

            print("connected")

        except:

            print("Couldn't establish a connection with the server")


    def get_state(self):

        self.socket_com.sendall(str.encode("GetState\r\n"))

        response = self.socket_com.recv(1024)

        response_decoded = response.decode("ascii")

        return str(response_decoded)


    def cap(self):

        self.socket_com.sendall(str.encode("StartCapping\r\n"))

        response = self.socket_com.recv(1024)

        response_decoded = response.decode("ascii")

        return str(response_decoded)


    def decap(self):

        self.socket_com.sendall(str.encode("StartDecapping\r\n"))

        response = self.socket_com.recv(1024)

        response_decoded = response.decode("ascii")

        return str(response_decoded)


    def disconnect(self):

        self.socket_com.close()


if __name__ == "__main__":

    print("Starting")

    decapper = Decapper()

    decapper.initialise("169.254.140.234", 10005)

    print("Initialised")

    print("Calling capping")

    response = decapper.decap()

    print("Called capping")

    print(response)

    decapper.disconnect()

    print("Disconnected")