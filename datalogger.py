import pathlib
from itertools import islice
import sys
from typing import Counter
from pathlib import Path
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import serial
import struct
from threading import Thread, Lock, Event
from collections import deque
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QFileDialog, QDialog,QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QPushButton, QTableWidget, QTableWidgetItem,QAbstractItemView ,
        QVBoxLayout, QWidget,QMessageBox)
from PyQt5.QtGui import QFont, QIcon
from datetime import datetime
from csv import writer, reader
# import serial
import functools
import os
import json
import serial.tools.list_ports
import signal
import time
look= Lock()
init_row = 0
data_array = deque(maxlen=1000)
stop_threads = True
stop_threads_1 = True 
flag_save = False
frame = ''

class Serial_com:
    def __init__(self, port, baud):
        self.ser= serial.Serial(port,baud,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
        timeout=(0.1))
        self.counter = 0 
        self.iteration = 0
        self.init_counter = 0       
        # Thread for reading serial Port
        self.t1 = Thread(target = self.loop)
        self.t1.start()
        self.t2 = Thread(target = self.record)
        self.t2.start()

    def loop (self):
        global data, flag_save, stop_threads
        while True:
            if stop_threads: 
                break            
            data = []
            # Waiting for serial buffer
            if self.ser.inWaiting() > 0:    
                res = self.ser.readline()
                # look.acquire()
                try:
                    trama = res[:-2].decode()
                    data = trama.split(",")
                    if len(data)==6 and flag_save:
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%fZ')[:-3]
                        data.insert(0,timestamp)
                        data_array.append(data)
                        frame.add_table(data)
                        self.counter = self.counter+1
                    # look.release()
                except Exception as error:
                    print(error)
        self.ser.close()    


    def record(self):
        while True:
            global flag_save, init_row
            if stop_threads: 
                break            
            if self.counter >=1000 and flag_save: 
                self.counter = 0
                data_save = deque(data_array)
                # frame.text_msg
                frame.text_msg.setText('Saving Data to file ...'+ frame.csv_name)
                with open(frame.csv_name, 'a+', newline='') as write_obj:    
                    # Create a writer object from csv module
                    csv_writer = writer(write_obj)
                    if self.iteration ==0 and init_row < 1:
                        csv_writer.writerow(['','Date Time','Channel1','Channel2','Channel3','Channel4','Channel5','Channel6'])
                    for i,x in enumerate(data_save):
                        # Add contents of list as last row in the csv file
                        x.insert(0,(i+1+init_row)+1000*self.iteration)
                        csv_writer.writerow(x)
                self.iteration = self.iteration +1 
                frame.text_msg.setText('Exporting file ...'+ frame.csv_name)
                
    def record_on_fail(self):
        global init_row
        new_slice = islice(data_array,len(data_array)- self.counter , len(data_array))
        data_save = deque(new_slice)
        frame.text_msg.setText('Saving Data to file ...'+ frame.csv_name)
        with open(frame.csv_name, 'a', newline='') as write_obj:    
            # Create a writer object from csv module
            csv_writer = writer(write_obj)
            if self.iteration ==0 and init_row < 1:
                csv_writer.writerow(['','Date Time','Channel1','Channel2','Channel3','Channel4','Channel5','Channel6'])

            for i,x in enumerate(data_save):
                # Add contents of list as last row in the csv file
                x.insert(0,(i+1+init_row)+1000*self.iteration)
                csv_writer.writerow(x)
            init_row = init_row + len(data_save) 
        self.iteration = self.iteration +1 
        frame.text_msg.setText('Exporting file ...'+ frame.csv_name)


    def record_on_exit(self):
        if len(data_array)!=0:
            new_slice = islice(data_array,len(data_array)- self.counter , len(data_array))
            data_save = deque(new_slice)
        # with open(frame.csv_name, 'a', newline='') as write_obj:    
        #     csv_writer = writer(write_obj)
        #     if self.iteration ==0:
        #         csv_writer.writerow(['','Date Time','Channel1','Channel2','Channel3','Channel4','Channel5','Channel6'])

        #     for i,x in enumerate(data_save):
        #         x.insert(0,(i+1)+1000*self.iteration)
        #         csv_writer.writerow(x)


class Screen(QWidget):
    def __init__(self, parent = None):
        super(Screen, self).__init__(parent)
        self.port_selec=''
        self.baud_selec='115200'
        self.choices=[]
        self.Serial = None
        self.path= os.path.join(os.path.abspath(os.getcwd()),'csv/')
        grid = QGridLayout()
        self.setLayout(grid)        
        grid.addWidget(self.serial_settings(), 0, 0,1,1)
        grid.addWidget(self.record_settings(), 1, 0,1,1)
        grid.addWidget(self.table_settings(),2,0,1,1)
        grid.addWidget(self.message(),3,0,1,2)
        grid.addWidget(self.table_data(), 0, 1,3,1)
        grid.setColumnStretch(1,5)        
        self.setLayout(grid)
        self.setWindowTitle('Datalogger')
        self.resize(1200,600)
        self.setAttribute(Qt.WA_DeleteOnClose)


    # ----------------------BOX SERIAL SETTINGS--------------------------------------------------
    def serial_settings(self):
        self.box_serial = QGroupBox("Serial Settings")
        text_port = QLabel("Port")        
        self.port = QComboBox()
        self.port.addItem("Choose a Port")

        self.ports = list(serial.tools.list_ports.comports())
        for i in self.ports:
            self.port.addItem(i.device)
        self.port.setCurrentText(self.port_selec)
        
        self.port.activated.connect(self.selec_port)

        text_baud = QLabel("Baudrate")
        self.baud = QComboBox()
        self.baud_array=['2400','4800','9600','19200','38400','57600','74880','115200','230400', '460800']
        for i in self.baud_array:
            self.baud.addItem(i)
        self.baud.setCurrentIndex(7 )
        self.baud.activated.connect(self.selec_baud)
        
        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self.onConnect)
        b1 = QVBoxLayout()
        b1.addWidget(text_port)
        b1.addWidget(self.port)
        b1.addWidget(text_baud)
        b1.addWidget(self.baud)
        b1.addStretch(1)
        b1.addWidget(self.connect_button) 

        self.box_serial.setLayout(b1)
        return self.box_serial
    # ----------------------RECORD SETTINGS--------------------------------------------------

    def record_settings(self):
        self.box_rec = QGroupBox("Record/Export")
        browse_text = QLabel("Folder Data")
        self.pathLine = QLineEdit(self.path)
        self.new_file_button = QPushButton('New File')
        self.new_file_button.setIcon(QIcon('assets/windows.jpeg'))
        self.new_file_button.clicked.connect(self.onBrowser)
        self.edit_button = QPushButton('Edit')
        self.edit_button.setIcon(QIcon('assets/windows.jpeg'))
        self.edit_button.clicked.connect(self.onFiles)
        # self.browse_button = QPushButton()
        # self.browse_button.clicked.connect(self.onBrowser)
        # self.browse_button.setIcon(QIcon('assets/windows.jpeg'))
        self.rec_button = QPushButton('REC') 
        self.rec_button.clicked.connect(self.onRec)
        self.rec_button.setIcon(QIcon('assets/record-16.png'))

        b3 = QHBoxLayout()
        b3.addWidget(self.new_file_button)
        b3.addWidget(self.edit_button)

        b2 = QHBoxLayout()
        b2.addWidget(self.pathLine)
        # b2.addWidget(self.browse_button)

        b1 = QVBoxLayout()
        b1.addWidget(browse_text)
        b1.addLayout(b3)
        b1.addStretch(1)
        b1.addWidget(QLabel("Check path before recording"))
        b1.addWidget(self.pathLine)
        b1.addStretch(1)
        b1.addStretch(1)
        b1.addWidget(self.rec_button)

        self.box_rec.setLayout(b1)
        return self.box_rec
    # ----------------------TABLE CONFIG--------------------------------------------------

    def table_settings(self):
        self.box_rec = QGroupBox("Table Settings")
        self.listCheckBox = ["Channel_1", "Channel_2", "Channel_3", "Channel_4", "Channel_5","Channel_6"]
        self.listLabel    = ['', '', '', '', '', '', '', '', '', '', ] 
        grid = QGridLayout()
        for i, v in enumerate(self.listCheckBox):
            self.listCheckBox[i] = QCheckBox(v)
            self.listCheckBox[i].setChecked(True)
            self.listCheckBox[i].stateChanged.connect(self.stateSlot)

            self.listLabel[i] = QLabel()
            grid.addWidget(self.listCheckBox[i], i, 0)
            grid.addWidget(self.listLabel[i],    i, 1)

        self.checkout_scroll = QCheckBox("Auto Scroll")
        self.checkout_scroll.stateChanged.connect(self.stateCHeckbow)
        b1= QVBoxLayout()
        b1.addWidget(self.checkout_scroll)
        b1.addStretch(1)
        b1.addLayout(grid)
        self.box_rec.setLayout(b1)
        return self.box_rec

    # ----------------------TABLE SETTINGS---------------------------------------------------        
    def table_data(self):
        self.box_rec = QGroupBox("Data")
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(['timestamp','CH 1','CH 2','CH 3','CH 4','CH 5','CH 6'])

        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setVisible(True)
        b1 = QHBoxLayout()
        b1.addWidget(self.tableWidget)
        self.box_rec.setLayout(b1)
        return self.box_rec
        
    # -------------------- MESSAGE SETTINGS -----------------------------------------------------      
    def message(self):
        self.box_msg = QGroupBox("Message Bar")

        text_1 = QLabel("Serial Comunication: ")
        text_1.setFont(QFont("Times",12,weight=QFont.Bold))

        self.ser_msg= QLabel("Close")
        self.ser_msg.setFont(QFont("Times",12,weight=QFont.Bold))
        self.ser_msg.setStyleSheet('color: #364958')
        
        text_2 = QLabel("Recording Data: ")
        text_2.setFont(QFont("Times",12,weight=QFont.Bold))

        self.text_msg = QLabel('Stop') 
        self.text_msg.setFont(QFont("Times",12,weight=QFont.Bold))
        self.text_msg.setStyleSheet('color: #364958')

        b1 = QHBoxLayout()
        b1.addWidget(text_1)
        b1.addWidget(self.ser_msg)
        b1.addStretch(1)
        b1.addWidget(text_2)
        b1.addWidget(self.text_msg)
        b1.addStretch(1)

        self.box_msg.setLayout (b1)
        return self.box_msg

    #---------------------- FUNCTIONS -------------------------------------------------
    def showDialog(self, text):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle("Alert")
        msgBox.setText(text)
        msgBox.setStandardButtons(QMessageBox.Ok )

        returnValue = msgBox.exec()
    
    def onRec(self,event):
        global flag_save
        # ------------ Function for export data
        if self.rec_button.text()=='REC':
            self.data_rec = datetime.timestamp(datetime.now())
            # self.data_rec = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            if '.csv' in self.pathLine.text():
                self.csv_name=self.pathLine.text()
            else:
                name = str(self.data_rec)+'.csv'
                print(os.path.join(self.pathLine.text(),"", name))
                self.csv_name= os.path.join(self.pathLine.text(),"", name)

            self.text_msg.setText('Collectind Data')
            flag_save = True
            self.rec_button.setText('STOP')
            # self.tableWidget.clear()
            self.new_file_button.setDisabled(True)
            self.edit_button.setDisabled(True)
            self.rec_button.setIcon(QIcon('assets/stop.jpeg'))
            if self.tableWidget.rowCount()>0:
                self.tableWidget.setRowCount(0)

        else:
            self.text_msg.setText('Stop')
            self.rec_button.setText('REC')        
            self.rec_button.setIcon(QIcon('assets/record-16.png'))
            self.new_file_button.setDisabled(False)
            self.edit_button.setDisabled(False)
            flag_save = False
            self.Serial.record_on_fail()
            if self.Serial:
                self.Serial.counter = 0
                self.Serial.iteration = 0
    # List COM availables 
    def List_port(self):
        self.port.clear()
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            self.port.addItem(p.device)

    # Get de Baudrate selected
    def selec_baud(self,text):
        self.baud_selec = self.baud.currentText() 
    
    # Get Port Selected 
    def selec_port(self,text):
        self.port_selec = self.port.itemText(text)
    
    def stateSlot(self):
        for i, v in enumerate(self.listCheckBox):
            self.tableWidget.setColumnHidden(i+1,not self.listCheckBox[i].isChecked())
    # @QtCore.pyqtSlot()

    def stateCHeckbow(self):
        
        self.auto_scroll_method()
    def auto_scroll_method(self):
        # print("Change value")
        QtCore.QTimer.singleShot(0,self.tableWidget.scrollToBottom)


    def add_table(self, data_array):
        # if self.tableWidget.rowCount()==1:
        #     self.tableWidget.resizeColumnsToContents()
        row = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(row+1)
        col = 0
        for item in data_array:
            cell = QTableWidgetItem(str(item))
            item =self.tableWidget.setItem(row, col, cell)
            col += 1
        if self.checkout_scroll.isChecked():
            self.auto_scroll_method()

    def onConnect(self, event):
        global stop_threads, flag_data 
        # Detect if the port was selected
        if self.connect_button.text()=='Connect':
            if(self.port_selec == '' or self.port_selec == 'Choose a port'):
                self.showDialog("Choose a valid port")
            else:
                # Start Serial protocol
                self.connect_button.setText('Disconnect')
                stop_threads = False
                try:
                    self.Serial=Serial_com(self.port_selec,self.baud_selec)                    
                    self.ser_msg.setText("Open")
                    # Disable the options for port and baudrate
                    self.port.setDisabled(True)
                    self.baud.setDisabled(True)  
                    self.pathLine.setDisabled(True)
                except Exception :
                    self.showDialog("Could not open selected port \n\n Please try again")

        else:
            self.connect_button.setText('Connect')
            stop_threads = True
            self.ser_msg.setText("Close")            
            self.port.setDisabled(False)
            self.baud.setDisabled(False)

    def onBrowser(self,event):
        path = QFileDialog.getExistingDirectory(self, 'Choose a Directory')
        if  self.path  != path and path is not None and path!="":
            self.path= os.path.abspath(path)
        if self.Serial:
            self.Serial.iteration=0
        global init_row
        init_row = 0
        self.pathLine.setText(self.path)

    def onFiles(self,event):
        global init_row
        path,__ = QFileDialog.getOpenFileName(self, 'Choose a File')
        if  self.path  != path and path is not None and path!="":
            self.path= path
            with open(self.path, 'r', newline='') as read_obj:    
                a =  read_obj.readlines()
                init_row = len(a)-1
        self.pathLine.setText(self.path)

    def closeEvent(self, event):

        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message', 
                        quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            global stop_threads, flag_save
            self.Serial.record_on_exit()
            stop_threads = True 
            flag_save = False
            event.accept()
        else:
            event.ignore()

    
def main():
    global stop_threads, flag_save, frame
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    frame = Screen()
    frame.show()
    # app.exec_()
    stop_threads = True 
    flag_save = False
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()