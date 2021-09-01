#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import sys
import traceback
from PyQt5.QtCore import QCoreApplication, QObject, QThreadPool, pyqtSignal, QRunnable, pyqtSlot
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QPushButton, QWidget

class ScannerSignals(QObject):

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    

class Decapper(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Decapper, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = ScannerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
            # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

class DecapperUI(QMainWindow):

    def __init__(self):

        # initial window setup
        super().__init__()

        "basic constructor"

        self.__readBuffer = ""

        self.socket_com = None

        self.__fs = None

        self.__connected = False

        self.initialise('169.254.140.234', 10005)

        # create a threadpool
        self.threadpool = QThreadPool()

        # call a function to setup the UI
        self.initUI()


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


    def decap(self, progress_callback):

        self.socket_com.sendall(str.encode("StartDecapping\r\n"))

        response = self.socket_com.recv(1024)

        response_decoded = response.decode("ascii")

        return str(response_decoded)


    def disconnect(self):

        self.socket_com.close()

    def decap_click_callback(self):
        decapper = Decapper(self.decap) # Any other args, kwargs are passed to the run function
        # decapper.signals.result.connect(self.scan_output)
        # decapper.signals.finished.connect(self.scan_complete)
        # decapper.signals.progress.connect(self.scan_progress)
        # decapper.signals.save.connect(self.save_file)
        # decapper.signals.num_scanned.connect(self.num_scanned_up)
        
        self.threadpool.start(decapper)

    def initUI(self):

        # setup of window
        self.setWindowTitle("Skenovací utilita")
        #self.setWindowIcon(QIcon((os.path.join(self.cwd, "img", "ic_scan.ico"))))
        #self.setStyle(QStyleFactory.create("Windows"))

        btn_decap = QPushButton("Start skenu", self)
        btn_decap.clicked.connect(self.decap_click_callback)
        # btn_decap.setEnabled(False)


        lyt_main = QHBoxLayout()
        lyt_main.addWidget(btn_decap)

        # final setup of the window
        widget = QWidget()
        widget.setLayout(lyt_main)
        self.setCentralWidget(widget)
        self.setFixedSize(1000,500)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = DecapperUI()
    frame.show()
    sys.exit(app.exec_())