#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import sys
import traceback
import os
import time
from typing import final
from PyQt5.QtCore import QCoreApplication, QObject, QThreadPool, Qt, pyqtSignal, QRunnable, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QProgressDialog, QPushButton, QSizePolicy, QSpinBox, QVBoxLayout, QWidget, QLineEdit

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

    __readBuffer = ""

    socket_com = None

    __fs = None

    __connected = False

    sb_num = None

    cycle_num = 0

    response_cycle = ""

    ip_address = ""
    port = ""
    status_bar = None
    btn_connect = None
    btn_disconnect = None
    le_port = None
    le_ip = None


    def __init__(self):

        # initial window setup
        super().__init__()

        # defining paths
        if getattr(sys, 'frozen', False):
            self.cwd = os.path.dirname(sys.executable)
        else:
            self.cwd = os.path.dirname(os.path.abspath(__file__))

        self.status_bar = self.statusBar()


        # create a threadpool
        self.threadpool = QThreadPool()

        # call a function to setup the UI
        self.initUI()

    # defining a function to be called when the user attempts to close the window
    def closeEvent(self, event):
        try:
            self.socket.close()
        except:
            pass
        sys.exit()


    def initialise(self, host, port):

        self.socket_com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:

            self.socket_com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.socket_com.connect((host, port))

            print("connected")

        except:

            print("Couldn't establish a connection with the server")


    def get_state(self, **progress_callback):

        response_decoded = ""

        socket_com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            socket_com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            socket_com.connect(('169.254.140.234', 10005))

            socket_com.sendall(str.encode("GetState\r\n"))


            response = socket_com.recv(1024)

            response_decoded = response.decode("ascii")

        except:
            traceback.print_exc()
            print("couldnt get state")

        try:
            socket_com.close()
        except:
            traceback.print_exc()
            print("couldnt disconnect")

        return str(response_decoded)


    def cap(self, progress_callback):

        response_decoded = ""

        socket_com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            socket_com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            socket_com.connect(('169.254.140.234', 10005))

            socket_com.sendall(str.encode("StartCapping\r\n"))

            progress_callback.emit(33)

            response = socket_com.recv(1024)

            response_decoded = response.decode("ascii")

            progress_callback.emit(66)

        except:
            traceback.print_exc()
            print("couldnt cap")

        try:
            socket_com.close()
        except:
            traceback.print_exc()
            print("couldnt disconnect")

        progress_callback.emit(100)

        return str(response_decoded)


    def decap(self, progress_callback):

        response_decoded = ""

        socket_com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            socket_com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            socket_com.connect(('169.254.140.234', 10005))

            socket_com.sendall(str.encode("StartDecapping\r\n"))

            progress_callback.emit(33)

            response = socket_com.recv(1024)

            response_decoded = response.decode("ascii")

            progress_callback.emit(66)

        except:
            traceback.print_exc()
            print("couldnt decap")

        try:
            socket_com.close()
        except:
            traceback.print_exc()
            print("couldnt disconnect")

        progress_callback.emit(100)

        return str(response_decoded)


    def cycle(self, cycle_num, progress_callback):
        print("cycle called")
        for i in range(1, cycle_num + 1):
            
            self.state_click_callback()

            print(self.response_cycle)
            
            while self.response_cycle != "2":
                self.response_cycle = self.state_click_callback()
                print(self.response_cycle)
                time.sleep(4)
            if self.response_cycle is not None and self.response_cycle != "":
                print("response in cycle is " + self.response_cycle)

            print("cycle " + str(i))

    # defining a function that creates a progress dialog
    def create_progress_dialog(self, title, text):
        self.pb_dialog = QProgressDialog(self)
        self.pb_dialog.setMinimum(0)
        self.pb_dialog.setLabelText(text)
        self.pb_dialog.setMaximum(100)
        self.pb_dialog.setValue(0)
        self.pb_dialog.setWindowTitle(title)
        self.pb_dialog.setCancelButton(None)
        self.pb_dialog.setModal(True)

    def action_progress(self, done_percentage):
        self.pb_dialog.setValue(done_percentage)

    def action_complete(self):
        self.action_progress(100)


    def cycle_output(self, string):
        self.response_cycle = string
        if self.response_cycle is not None:
            print("the response is " + self.response_cycle)

    def action_output(self, string):
        print(string)

    def decap_click_callback(self):
        
        decapper = Decapper(self.decap) # Any other args, kwargs are passed to the run function
        decapper.signals.result.connect(self.action_output)
        decapper.signals.finished.connect(self.action_complete)
        decapper.signals.progress.connect(self.action_progress)
        self.create_progress_dialog("DECAPPING", "Decapping running, please wait")  
        self.action_progress(0)
        self.pb_dialog.show()
        self.threadpool.start(decapper)

    def cap_click_callback(self):

        decapper = Decapper(self.cap) # Any other args, kwargs are passed to the run function
        decapper.signals.result.connect(self.action_output)
        decapper.signals.finished.connect(self.action_complete)
        decapper.signals.progress.connect(self.action_progress)
        self.create_progress_dialog("CAPPING", "Capping running, please wait")  
        self.action_progress(0)
        self.pb_dialog.show()
        self.threadpool.start(decapper)

    def state_click_callback(self, *progress_callback):
        decapper = Decapper(self.get_state) # Any other args, kwargs are passed to the run function
        decapper.signals.result.connect(self.cycle_output)
        # decapper.signals.finished.connect(self.action_complete)
        # decapper.signals.progress.connect(self.action_progress)
        # decapper.signals.save.connect(self.save_file)
        # decapper.signals.num_scanned.connect(self.num_scanned_up)
        # self.create_progress_dialog("CAPPING", "Capping running, please wait")  
        # self.action_progress(0)
        # self.pb_dialog.show()
        self.threadpool.start(decapper)

    def btn_ip_callback(self):

        try:
            socket.inet_aton(self.le_ip.text())
            self.ip_address = self.le_ip.text()
            self.port = self.le_port.text()
            self.status_bar.showMessage("IP address was set to " + self.ip_address + ":" + self.port)
        except socket.error:
            self.status_bar.showMessage("IP address is in an incorrect format")

    def btn_connect_callback(self):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.ip_address, self.port))
            self.status_bar.showMessage("Connected to recapper at " + self.ip_address + ":" + self.port)
            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(False)
        except:
            self.status_bar.showMessage("Could not connect to recapper at " + self.ip_address + ":" + self.port)
            

    def sp_num_callback(self):
        self.cycle_num = self.sb_num.value()
        
    def cycle_click_callback(self):

        if self.cycle_num > 0:

            decapper = Decapper(self.cycle, self.cycle_num) # Any other args, kwargs are passed to the run function
            decapper.signals.result.connect(self.cycle_output)
            decapper.signals.finished.connect(self.action_complete)
            decapper.signals.progress.connect(self.action_progress)
            # decapper.signals.save.connect(self.save_file)
            # decapper.signals.num_scanned.connect(self.num_scanned_up)
            self.create_progress_dialog("CYCLING", "Capping running, please wait")  
            # self.action_progress(0)
            # self.pb_dialog.show()
            self.threadpool.start(decapper)

    def initUI(self):

        # setup of window
        self.setWindowTitle("Recapper remote controller")
        #self.setWindowIcon(QIcon((os.path.join(self.cwd, "ic_scan.ic"))))

        # define a label to hold an image
        lbl_logo = QLabel(self)
        im_logo = QPixmap(os.path.join(self.cwd, "img", "logo_db.png"))
        lbl_logo.setPixmap(im_logo.scaled(500, 300, Qt.KeepAspectRatio))
        lbl_logo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        lbl_ip = QLabel(self)
        lbl_ip.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        lbl_ip.setText("IP Address")

        lbl_port = QLabel(self)
        lbl_port.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        lbl_port.setText("Port")


        self.le_ip = QLineEdit()

        self.le_port = QLineEdit()

        btn_ip = QPushButton()
        btn_ip.setText("Save IP Address and port")
        btn_ip.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn_ip.clicked.connect(self.btn_ip_callback)

        lyt_ip = QHBoxLayout()
        lyt_ip.addWidget(lbl_ip)
        lyt_ip.addWidget(self.le_ip)
        lyt_ip.addWidget(lbl_port)
        lyt_ip.addWidget(self.le_port)
        lyt_ip.addWidget(btn_ip)

        self.btn_connect = QPushButton()
        self.btn_connect.setText("Connect")
        self.btn_connect.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_connect.clicked.connect(self.btn_connect_callback)

        self.btn_disconnect = QPushButton()
        self.btn_disconnect.setText("Disconnect")
        self.btn_disconnect.setEnabled(False)
        self.btn_disconnect.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        lyt_connection = QHBoxLayout()
        lyt_connection.addWidget(self.btn_connect)
        lyt_connection.addWidget(self.btn_disconnect)

        btn_decap = QPushButton("Decap vials", self)
        btn_decap.clicked.connect(self.decap_click_callback)
        btn_decap.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # btn_decap.setEnabled(False)

        btn_cap = QPushButton("Cap vials", self)
        btn_cap.clicked.connect(self.cap_click_callback)
        btn_cap.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # btn_decap.setEnabled(False)

        lyt_capping = QHBoxLayout()
        lyt_capping.addWidget(btn_cap)
        lyt_capping.addWidget(btn_decap)

        self.sb_num = QSpinBox()
        self.sb_num.valueChanged.connect(self.sp_num_callback)

        btn_state = QPushButton("CYCLE", self)
        btn_state.clicked.connect(self.cycle_click_callback)

        lyt_up = QHBoxLayout()
        # lyt_up.setAlignment(Qt.AlignCenter)
        lyt_up.addWidget(lbl_logo)


        lyt_main = QVBoxLayout()
        lyt_main.setContentsMargins(100, 100, 100, 100)
        lyt_main.setAlignment(Qt.AlignCenter)
        lyt_main.addLayout(lyt_up, 2)
        lyt_main.addSpacing(100)
        lyt_main.addLayout(lyt_ip)
        lyt_main.addSpacing(50)
        lyt_main.addLayout(lyt_connection)
        lyt_main.addSpacing(50)
        lyt_main.addLayout(lyt_capping)
        lyt_main.addWidget(self.sb_num)
        lyt_main.addWidget(btn_state)


        # final setup of the window
        widget = QWidget()
        widget.setLayout(lyt_main)
        self.setCentralWidget(widget)
        #self.setFixedSize(1000,500)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = DecapperUI()
    frame.show()
    sys.exit(app.exec_())
