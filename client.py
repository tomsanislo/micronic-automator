#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import sys
import traceback
import os
import time
from PyQt5.QtCore import QObject, QThreadPool, Qt, pyqtSignal, QRunnable, pyqtSlot
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow, QMenuBar, QMessageBox, QProgressDialog, QPushButton, QSizePolicy, QSpinBox, QVBoxLayout, QWidget, QLineEdit

class ShouldRun():
    should_run = True

    def get_should(self):
        return self.should_run
    def kill_cycle(self):
        print("called kill")
        self.should_run = False
    

class ScannerSignals(QObject):

    finished = pyqtSignal()
    error = pyqtSignal(object)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    cap = pyqtSignal()
    decap = pyqtSignal()


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
        self.kwargs['error_callback'] = self.signals.error
        self.kwargs['cap_callback'] = self.signals.cap
        self.kwargs['decap_callback'] = self.signals.decap

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


    sb_num = None

    cycle_num = 0

    response_cycle = ""

    ip_address = ""
    port = ""
    status_bar = None
    btn_connect = None
    btn_disconnect = None
    btn_cap = None
    btn_decap = None
    le_port = None
    le_ip = None
    lbl_state = None
    sck = None
    btn_cycle = None
    event_stop = None
    varholder = None
    should_run = True


    def __init__(self):

        # initial window setup
        super().__init__()

        self.create_menu_bar()
        menu_bar = self.menuBar()

        # defining paths
        if getattr(sys, 'frozen', False):
            self.cwd = os.path.dirname(sys.executable)
        else:
            self.cwd = os.path.dirname(os.path.abspath(__file__))

        self.status_bar = self.statusBar()


        # create a threadpool
        self.threadpool = QThreadPool()

        self.should_run = ShouldRun()


        # call a function to setup the UI
        self.initUI()

    # defining a function to be called when the user attempts to close the window
    def closeEvent(self, *event):
        try:
            self.sck.close()
        except:
            print(traceback.format_exc())
        sys.exit()


    def create_menu_bar(self):
        menu_bar = QMenuBar(self)
        file_menu = menu_bar.addMenu("&File")
        edit_menu = menu_bar.addMenu("&Edit")
        help_menu = menu_bar.addMenu("&Help")

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        file_menu.triggered[QAction].connect(self.file_called)
        file_menu.addAction(quit_action)

        help_action = QAction("&Info", self)
        # help_action.setShortcut("Ctrl+Q")
        help_menu.triggered[QAction].connect(self.help_called)
        help_menu.addAction(help_action)

        self.setMenuBar(menu_bar)

    def file_called(self, action):
        if action.text() == "&Quit":
            self.closeEvent()
            
    def help_called(self, action):
        if action.text() == "&Info":
            self.show_success("2021 - \nDIANA Biotechnologies\n\nKontakt:\nTomas Sanislo\ntomas.sanislo@dianalab.cz\n775 960 726")

    # defining a function that shows error message
    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message[1])
        msg.setWindowIcon(QIcon((os.path.join(self.cwd, "img", "icon.png"))))
        msg.setWindowTitle("Chyba")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("color: black")
        msg.exec_()

    # defining a function that shows a success message
    def show_success(self, message):
        msg = QMessageBox()
        msg.setIconPixmap(QPixmap(os.path.join(self.cwd, "img", "logo_db_medium.png")).scaled(100, 50, Qt.KeepAspectRatio))
        msg.setText(message)
        msg.setWindowIcon(QIcon((os.path.join(self.cwd, "img", "icon.png"))))
        msg.setWindowTitle("Hotovo")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("background-color: white;")
        msg.exec_()


    def cap(self, progress_callback, error_callback, cap_callback, decap_callback):

        response_decoded = ""

        print("capping in progress")

        try:

            self.sck.sendall(str.encode("StartCapping\r\n"))

            # progress_callback.emit(33)

            response = self.sck.recv(1024)

            response_decoded = response.decode("ascii")

            # progress_callback.emit(66)

        except:

            error_callback.emit("Error - Error in decapping of vials")
            
        # progress_callback.emit(100)

        # return str(response_decoded)


    def decap(self, progress_callback, error_callback, cap_callback, decap_callback):

        response_decoded = ""

        try:

            self.sck.sendall(str.encode("StartDecapping\r\n"))

            # progress_callback.emit(33)

            response = self.sck.recv(1024)

            response_decoded = response.decode("ascii")

            # progress_callback.emit(66)

        except:

            error_callback.emit("Error - Error in decapping of vials")
            
        # progress_callback.emit(100)

        # return str(response_decoded)



    def cycle(self, cycle_num, lbl_state, sck, should_run, progress_callback, error_callback, cap_callback, decap_callback):

        print("entering cycling")

        for i in range(1, cycle_num + 1):

            if not should_run.get_should():
                print("should have killed myself")
                break
            else:
                print("should is on")

            print("in cycle " + str(i))
            
            progress_callback.emit(i)

            response = ""

            while True:

                response = ""


                try:
                    sck.sendall(b"GetState\r\n")
                    response_coded = sck.recv(1024)
                    response = response_coded.decode("ascii")[:1]

                except:
                    error_callback.emit("Error - Error in getting state of recapper")

                print("the response is" + str(response))

                time.sleep(2)

                if response == str(1):
                    break
                if response == str(4):
                    break
                
                if not should_run.get_should():
                    print("should have killed myself in whie")
                    break
                else:
                    print("should is on in while")

                

            response = ""

            try:
                sck.sendall(b"GetState\r\n")
                response_coded = sck.recv(1024)
                response = response_coded.decode("ascii")[:1]

            except:
                error_callback.emit("Error - Error in getting state of recapper")

            print("the response is" + str(response))

            if response == str(4):
                lbl_state.setText("Capping")
                lbl_state.setStyleSheet("background-color: yellow; color: black; font: bold")
                cap_callback.emit()
                print("capping")
                time.sleep(15)


            if response == str(1):
                lbl_state.setText("Decapping")
                lbl_state.setStyleSheet("background-color: blue; color: white; font: bold")
                decap_callback.emit()
                print("decapping")
                time.sleep(15)

            response = ""

            while True:

                time.sleep(2)

                response = ""

                try:
                    sck.sendall(b"GetState\r\n")
                    response_coded = sck.recv(1024)
                    response = response_coded.decode("ascii")[:1]

                except:
                    error_callback.emit("Error - Error in getting state of recapper")

                print("the response is" + str(response))


                if response == str(1):
                    break
                if response == str(4):
                    break
                
                if not should_run.get_should():
                    print("should have killed myself in whie")
                    break
                else:
                    print("should is on in while")

                


                
            response = ""

            try:
                sck.sendall(b"GetState\r\n")
                response_coded = sck.recv(1024)
                response = response_coded.decode("ascii")[:1]

            except:
                error_callback.emit("Error - Error in getting state of recapper")

            print("the response is" + str(response))

            if response == str(4):
                lbl_state.setText("Capping")
                lbl_state.setStyleSheet("background-color: yellow; color: black; font: bold")
                cap_callback.emit()
                print("capping")
                time.sleep(15)


            if response == str(1):
                lbl_state.setText("Decapping")
                lbl_state.setStyleSheet("background-color: blue; color: white; font: bold")
                decap_callback.emit()
                print("decapping")
                time.sleep(15)
 

               

            
            


    # defining a function that creates a progress dialog
    def create_progress_dialog(self, title, text, num_cycle):
        self.pb_dialog = QProgressDialog(self)
        btn_pbd = QPushButton()
        btn_pbd.setText("Stop cycle")
        self.pb_dialog.setMinimum(0)
        self.pb_dialog.setLabelText(text)
        self.pb_dialog.setMaximum(num_cycle)
        self.pb_dialog.setValue(1)
        self.pb_dialog.setWindowTitle(title)
        lbl_img = QLabel(self)
        im_logo = QPixmap(os.path.join(self.cwd, "img", "cycle.png"))
        lbl_img.setPixmap(im_logo.scaled(50,50,Qt.KeepAspectRatio))
        lbl_img.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        lbl_img.setAlignment(Qt.AlignCenter)
        self.pb_dialog.setLabel(lbl_img)
        self.pb_dialog.setCancelButton(btn_pbd)
        self.pb_dialog.setModal(True)


    def action_progress(self, done_cycle):
        self.pb_dialog.setValue(done_cycle)

    def action_complete(self):
        self.pb_dialog = None


    def cycle_output(self, string):
        self.response_cycle = string
        if self.response_cycle is not None:
            print("the response is " + self.response_cycle)

    def action_output(self, string):
        print(string)

    def decap_click_callback(self):
        
        decapper = Decapper(self.decap) # Any other args, kwargs are passed to the run function
        # decapper.signals.result.connect(self.action_output)
        # decapper.signals.finished.connect(self.action_complete)
        # decapper.signals.progress.connect(self.action_progress)
        decapper.signals.error.connect(self.show_error)
        # self.create_progress_dialog("DECAPPING", "Decapping running, please wait")  
        # self.action_progress(0)
        # self.pb_dialog.show()
        self.threadpool.start(decapper)

    def cap_click_callback(self):

        decapper = Decapper(self.cap) # Any other args, kwargs are passed to the run function
        # decapper.signals.result.connect(self.action_output)
        # decapper.signals.finished.connect(self.action_complete)
        # decapper.signals.progress.connect(self.action_progress)
        decapper.signals.error.connect(self.show_error)
        # self.create_progress_dialog("CAPPING", "Capping running, please wait")  
        # self.action_progress(0)
        # self.pb_dialog.show()
        self.threadpool.start(decapper)


    def btn_ip_callback(self):

        try:
            if self.le_port.text().isdecimal():
                socket.inet_aton(self.le_ip.text())
                self.ip_address = self.le_ip.text()
                self.port = self.le_port.text()
                self.status_bar.showMessage("IP address was set to " + self.ip_address + ":" + self.port)
                self.btn_connect.setEnabled(True)
            else:
                self.status_bar.showMessage("Please enter a valid port number")
        except socket.error:
            self.status_bar.showMessage("IP address is in an incorrect format")

    def btn_connect_callback(self):

        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sck.connect((self.ip_address, int(self.port)))
            self.status_bar.showMessage("Connected to recapper at " + self.ip_address + ":" + self.port)
            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(True)
            self.btn_cap.setEnabled(True)
            self.btn_decap.setEnabled(True)
            self.lbl_state.setText("Connected")
            self.lbl_state.setStyleSheet("background-color: green; color: white; font: bold")
            self.sb_num.setEnabled(True)
            self.btn_cycle.setEnabled(True)

        except:
            print(traceback.format_exc())
            self.status_bar.showMessage("Could not connect to recapper at " + self.ip_address + ":" + self.port)

    def btn_disconnect_callback(self):

        try:
            self.sck.()
            self.status_bar.showMessage("Disconnected from recapper")
            self.btn_connect.setEnabled(True)
            self.btn_disconnect.setEnabled(False)
            self.btn_cap.setEnabled(False)
            self.btn_decap.setEnabled(False)
            self.lbl_state.setText("Disconnected")
            self.lbl_state.setStyleSheet("background-color: red; color: white; font: bold")
            self.sb_num.setEnabled(False)
            self.btn_cycle.setEnabled(False)
            print("disconnected")


        except:
            self.status_bar.showMessage("Could not disconnect from recapper")
            

    def sp_num_callback(self):
        self.cycle_num = self.sb_num.value()


    def cycle_callback(self):

        if self.cycle_num > 0:

            decapper = Decapper(self.cycle, self.cycle_num, self.lbl_state, self.sck, self.should_run) # Any other args, kwargs are passed to the run function
            decapper.signals.result.connect(self.cycle_output)
            decapper.signals.finished.connect(self.action_complete)
            decapper.signals.progress.connect(self.action_progress)
            decapper.signals.error.connect(self.show_error)
            decapper.signals.cap.connect(self.cap_click_callback)
            decapper.signals.decap.connect(self.decap_click_callback)
            self.create_progress_dialog("CYCLING", "Capping running, please wait", self.cycle_num)
            print("creating progress dialog")
            self.pb_dialog.show()
            self.pb_dialog.canceled.connect(self.should_run.kill_cycle)
            self.threadpool.start(decapper)

    def initUI(self):

        # setup of window
        self.setWindowTitle("Recapper Remote Controller")
        self.setWindowIcon(QIcon(os.path.join(self.cwd, "img", "icon.png")))
        self.setFont(QFont('Arial', 11))

        lbl_state_title = QLabel(self)
        lbl_state_title.setText("State:")
        lbl_state_title.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        self.lbl_state = QLabel(self)
        self.lbl_state.setText("Disconnected")
        self.lbl_state.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lbl_state.setStyleSheet("background-color: red; color: white; font: bold")
        self.lbl_state.setContentsMargins(7,5,7,5)

        lyt_state = QHBoxLayout()
        lyt_state.addWidget(lbl_state_title)
        lyt_state.addWidget(self.lbl_state)
        
        # define a label to hold an image
        lbl_logo = QLabel(self)
        im_logo = QPixmap(os.path.join(self.cwd, "img", "logo_db_medium.png"))
        lbl_logo.setPixmap(im_logo)
        lbl_logo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        lbl_ip = QLabel(self)
        lbl_ip.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        lbl_ip.setText("IP Address")

        lbl_port = QLabel(self)
        lbl_port.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        lbl_port.setText("Port")


        self.le_ip = QLineEdit()
        self.le_ip.returnPressed.connect(self.btn_ip_callback)

        self.le_port = QLineEdit()
        self.le_port.returnPressed.connect(self.btn_ip_callback)

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
        self.btn_connect.setEnabled(False)

        self.btn_disconnect = QPushButton()
        self.btn_disconnect.setText("Disconnect")
        self.btn_disconnect.setEnabled(False)
        self.btn_disconnect.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_disconnect.clicked.connect(self.btn_disconnect_callback)

        lyt_connection = QHBoxLayout()
        lyt_connection.addWidget(self.btn_connect)
        lyt_connection.addWidget(self.btn_disconnect)

        self.btn_decap = QPushButton("Decap vials", self)
        self.btn_decap.clicked.connect(self.decap_click_callback)
        self.btn_decap.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_decap.setEnabled(False)

        self.btn_cap = QPushButton("Cap vials", self)
        self.btn_cap.clicked.connect(self.cap_click_callback)
        self.btn_cap.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_cap.setEnabled(False)

        lyt_capping = QHBoxLayout()
        lyt_capping.addWidget(self.btn_cap)
        lyt_capping.addWidget(self.btn_decap)

        self.sb_num = QSpinBox()
        self.sb_num.valueChanged.connect(self.sp_num_callback)
        self.sb_num.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.sb_num.setMaximumWidth(200)
        self.sb_num.setAlignment(Qt.AlignCenter)
        self.sb_num.setEnabled(False)

        self.btn_cycle = QPushButton("Start a cycle", self)
        self.btn_cycle.clicked.connect(self.cycle_callback)
        self.btn_cycle.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_cycle.setEnabled(False)

        lyt_cycle = QHBoxLayout()
        lyt_cycle.addWidget(self.sb_num)
        lyt_cycle.addWidget(self.btn_cycle)

        lyt_up = QVBoxLayout()
        lyt_up.setAlignment(Qt.AlignCenter)
        lyt_up.addWidget(lbl_logo)
        lyt_up.addSpacing(100)
        lyt_up.addLayout(lyt_state)

        hline_main = QFrame(self)
        hline_main.setFrameShape(QFrame.HLine)
        hline_main.setFrameShadow(QFrame.Sunken)
        hline_main.setLineWidth(2)

        hline_ip = QFrame(self)
        hline_ip.setFrameShape(QFrame.HLine)
        hline_ip.setFrameShadow(QFrame.Sunken)
        hline_ip.setLineWidth(2)

        hline_connection = QFrame(self)
        hline_connection.setFrameShape(QFrame.HLine)
        hline_connection.setFrameShadow(QFrame.Sunken)
        hline_connection.setLineWidth(2)

        hline_man = QFrame(self)
        hline_man.setFrameShape(QFrame.HLine)
        hline_man.setFrameShadow(QFrame.Sunken)
        hline_man.setLineWidth(2)

        


        lyt_main = QVBoxLayout()
        lyt_main.setContentsMargins(50, 50, 50, 25)
        lyt_main.setAlignment(Qt.AlignCenter)
        lyt_main.addLayout(lyt_up)
        lyt_main.addSpacing(50)
        lyt_main.addWidget(hline_main)
        lyt_main.addSpacing(25)
        lyt_main.addLayout(lyt_ip)
        lyt_main.addSpacing(25)
        lyt_main.addWidget(hline_ip)
        lyt_main.addSpacing(25)
        lyt_main.addLayout(lyt_connection)
        lyt_main.addSpacing(25)
        lyt_main.addWidget(hline_connection)
        lyt_main.addSpacing(25)
        lyt_main.addLayout(lyt_capping)
        lyt_main.addSpacing(25)
        lyt_main.addWidget(hline_man)
        lyt_main.addSpacing(25)
        lyt_main.addLayout(lyt_cycle)


        # final setup of the window
        widget = QWidget()
        widget.setLayout(lyt_main)
        self.setCentralWidget(widget)
        # self.showMaximized()
        # self.setFixedSize(600,650)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = DecapperUI()
    frame.show()
    sys.exit(app.exec_())
