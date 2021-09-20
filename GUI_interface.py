from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget,QMainWindow, QHeaderView,QMessageBox)
from PyQt5.QtGui import QFont
import datetime
# import serial
import os
import serial.tools.list_ports

class Screen(QWidget):
    def __init__(self, parent = None):
        super(Screen, self).__init__(parent)
        self.port_selec=''
        self.baud_selec='115200'
        self.choices=[]
        self.y_max = 100
        self.y_min = 0
        self.path_dir = 'C:'
        self.data_rec=''
        self.time_upd= 0.5
        self.port = ''
        self.path= os.path.abspath(os.getcwd())
        grid = QGridLayout()
        self.setLayout(grid)
        
    
        grid.addWidget(self.serial_settings(), 0, 0,2,1)
        grid.setColumnStretch(0,0 )
        # grid.addWidget(self.plot_settings(), 1, 0,3,1)
        grid.addWidget(self.message(),2,0,1,2)

        grid.addWidget(self.table_data(), 0, 1,1,3)
        grid.setColumnStretch(1, 5)        
        self.setLayout(grid)

        self.setWindowTitle('Datalogger')
        self.show()


# ----------------------BOX SERIAL SETTINGS--------------------------------------------------
    def serial_settings(self):
        self.box_serial = QGroupBox("Serial Settings")
        text_port = QLabel("Port")        
        self.port = QComboBox()
        # if(settings['port'] == ""):
        self.port_selec =""
        self.port.addItem("Choose a Port")
        # else:
        #     self.port_selec = settings['port']

        self.ports = list(serial.tools.list_ports.comports())
        for i in self.ports:
            self.port.addItem(i.device)

        self.port.activated.connect(self.selec_port)
    
        text_baud = QLabel("Baudrate")
        self.baud = QComboBox()
        self.baud_array=['2400','4800','9600','19200','38400','57600','74880'
        ,'115200','230400', '460800']
        for i in self.baud_array:
            self.baud.addItem(i)
        self.baud.setCurrentIndex(7 )
        self.baud.activated.connect(self.selec_baud)
        # self.baud.setStyleSheet('background-color: white')
        
        self.connect_button = QPushButton('Connect')
        # self.connect_button.clicked.connect(self.onConnect)
        # self.connect_button.setStyleSheet('background-color: #F2F2F2')


        browse_text = QLabel("Folder Data")
        self.pathLine = QLineEdit(self.path)
        self.browse_button = QPushButton('Browser')

        # b2 = QHBoxLayout()
        # b2.addWidget(self.pathLine)
        # b2.addWidget(self.browse_button)


        b1 = QVBoxLayout()
        b1.addWidget(text_port)
        b1.addWidget(self.port)
        b1.addStretch(1)
        b1.addWidget(text_baud)
        b1.addWidget(self.baud)
        b1.addStretch(2)
        b1.addWidget(self.connect_button) 
        b1.addStretch(1)
        b1.addWidget(browse_text)
        # b1.addLayout(b2)
        b1.addWidget(self.pathLine)
        b1.addWidget(self.browse_button)
        
        # self.box_serial.setStyleSheet("background-color: #F1F7EE")
        self.box_serial.setLayout(b1)
        return self.box_serial

# ----------------------TABLE SETTINGS---------------------------------------------------        
    def table_data(self):
        self.box_rec = QGroupBox("Data")
        self.tableWidget = QTableWidget()
        # set row count
        # self.tableWidget.setRowCount(4)

        # set column count
        # self.tableWidget.setColumnCount(7)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.rec_button.clicked.connect(self.onRec)
        # self.rec_button.setStyleSheet('background-color: #F2F2F2')
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        b1 = QHBoxLayout()
        b1.addWidget(self.tableWidget)

        # b1.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.box_rec.setLayout(b1)
        # self.box_rec.setStyleSheet("background-color: #F1F7EE")
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
    def showDialog(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle("Alert")
        msgBox.setText("Choose a valid port")
        msgBox.setStandardButtons(QMessageBox.Ok )

        returnValue = msgBox.exec()
    
    # def onRec(self,event):
    #     # ------------ Function for export data
    #     if self.rec_button.text()=='REC':
    #         self.data_rec = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    #         self.text_msg.setText('Exporting file ...'+ self.data_rec+'.csv')
    #         # f=self.path_dir+"\\"+self.data_rec+'.csv'
    #         f='csv/'+self.data_rec+'.csv'
            
    #         # Create CSV file
    #         with open(f, 'w') as write_obj:
    #         # Create a writer object from csv module
    #             csv_writer = writer(write_obj)
    #         # Add header to the csv file
    #             csv_writer.writerow(['','Date Time','Photodiode_A_Max','Photodiode_A_Min','Photodiode_B','Calibrated_B'])
    #         global flag_save
    #         flag_save = True
    #         self.rec_button.setText('STOP')
    #     else:
    #         global line
    #         self.text_msg.setText('Stop')
    #         self.rec_button.setText('REC')        
    #         flag_save = False
    #         line = 1

    # List COM availables 
    def List_port(self):
        self.port.clear()
        ports = list(serial.tools.list_ports.comports())
        lst = []
        for p in ports:
            self.port.addItem(p.device)

    # Get de Baudrate selected
    def selec_baud(self,text):
        self.baud_selec = self.baud.currentText() 
    
    # Get Port Selected 
    def selec_port(self,text):
        self.port_selec = self.port.itemText(text)
        self.port= self.port_selec
        # with open ('settings.json','w') as _file:
        #     json.dump(settings,_file)
    



if __name__ == '__main__':
    # data = DataPlot()
    # GUI panel
    app = QApplication([])
    frame = Screen()
    app.exec_()
    # stop_threads_1 = True 
    # stop_threads = True 
