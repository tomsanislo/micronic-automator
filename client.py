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

            socket_com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            socket_com.connect((host, port))

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

    decapper.initialise("169.254.88.108", 1005)

    print("Initialised")

    print("Calling decapping")

    response = decapper.decap()

    print("Called decapping")

    print(response)

    decapper.disconnect()

    print("Disconnected")