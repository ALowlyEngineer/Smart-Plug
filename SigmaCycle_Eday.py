#!/usr/bin/python

import sys,os
import time
import Adafruit_ADS1x15 
import sqlite3
from PyQt4 import QtGui, QtCore     
from scipy.interpolate import interp1d  
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import random
import serial

time1= [0,1,2,3,4,5]
power= [0,1,2,3,4,5]

start= time.time()
conn = sqlite3.connect(':memory:')
c = conn.cursor()
c.execute("""CREATE TABLE pedaling(power real, time real)""")
c.execute("SELECT * FROM pedaling WHERE time != 0")
#print(c.fetchall())
conn.commit()
#print("Database created")

ser = serial.Serial('/dev/ttyS0')  # open serial port
ser.baudrate = 9600
#print(ser.name)         # check which port was really used
   
     


class DataWindow(QtGui.QMainWindow):
    def __init__(self):
        super(DataWindow, self).__init__()
        self.screen = QtGui.QDesktopWidget().screenGeometry()
        self.center = QtGui.QDesktopWidget().screenGeometry().center()
        self.setWindowTitle("SigmaCycle")
        self.setWindowIcon(QtGui.QIcon('/home/pi/Logo.jpg'))
        self.setStyleSheet("background-color: white;")
        newfont = QtGui.QFont("Times",30, QtGui.QFont.Bold)
        bold2font = QtGui.QFont("Times",20, QtGui.QFont.Bold)
        readfont = QtGui.QFont("Times", 22)
        addedfont = QtGui.QFont("Times", 20)
        self.buttonFont = QtGui.QFont("Times",25,QtGui.QFont.Bold)
        self.pressedFont = QtGui.QFont("Times",25)
##        self.volt_value = 7
        self.ratioFactor = 25*(2.048/32767)

        # Set up interpolation function
        self.voltage_data = [0,6.76,6.99,7.39,8.2,8.26,8.93,9.15,9.55,10.3,10.8,11.4,11.7,11.9,12.3,13.2,14.5,15,15.6,16.6,20.2,21.9,24.3,24.7,26.2,27.8]
        self.current_data = [0,20,21.3,25.5,41.5,43,59.7,65.3,75.1,98.5,112,132,141,147,159,187,227,248,265,297,422,481,599,622,678,729]
        self.f = interp1d(self.voltage_data,self.current_data)

        # Setup ADC
        self.adc = Adafruit_ADS1x15.ADS1115()
        self.GAIN = 2

       
        # Timer
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer,QtCore.SIGNAL("timeout()"),self.update_data)

        
        # Voltage Box
        self.volt_label = QtGui.QLabel(self)
        self.volt_label.resize(200,75)
        self.volt_label.setText("Voltage")
        self.volt_label.setFont(newfont)
        self.volt_label.move(0.05*self.screen.width(),0.3*self.screen.height()-100)
        self.volt_read = QtGui.QLabel(self)
        self.volt_read.resize(300,75)
        self.volt_read.setText("0  V")
        self.volt_read.setFont(readfont)
        self.volt_read.move(0.08*self.screen.width(),0.3*self.screen.height())


        # Power Box
        self.power_label = QtGui.QLabel(self)
        self.power_label.resize(175,75)
        self.power_label.setText("Power")
        self.power_label.setFont(newfont)
        self.power_label.move(0.8*self.screen.width()-50,0.3*self.screen.height()-100)
        self.power_read = QtGui.QLabel(self)
        self.power_read.resize(300,75)
        self.power_read.setText("0  W")
        self.power_read.setFont(readfont)
        self.power_read.move(0.8*self.screen.width(),0.47*self.screen.height()-30)

        # Current Box
        self.curr_label = QtGui.QLabel(self)
        self.curr_label.resize(200,75)
        self.curr_label.setText("Current")
        self.curr_label.setFont(newfont)
        self.curr_label.move(0.5*self.screen.width()-90,0.3*self.screen.height()-100)
        self.curr_read = QtGui.QLabel(self)
        self.curr_read.resize(500,75)
        self.curr_read.setText("0  A")
        self.curr_read.setFont(readfont)
        self.curr_read.move(0.36*self.screen.width(),0.3*self.screen.height())
       

        
         # Cost Box
        self.cost_label = QtGui.QLabel(self)
        self.cost_label.resize(150,150)
        self.cost_label.setText("Cost:")
        self.cost_label.setFont(bold2font)
        self.cost_label.move(0.05*self.screen.width(),0.5*self.screen.height()) 
        self.cost_read = QtGui.QLabel(self)
        self.cost_read.resize(150,150)
        self.cost_read.setText("$0")
        self.cost_read.setFont(addedfont)
        self.cost_read.move(0.2*self.screen.width(),0.5*self.screen.height())   

       # Calorie Box   (kcal)
        self.cal_label= QtGui.QLabel(self)
        self.cal_label.resize(150,150)
        self.cal_label.setText("Calories:")
        self.cal_label.setFont(bold2font)
        self.cal_label.move(0.4*self.screen.width(),0.5*self.screen.height()) 
        self.cal_read = QtGui.QLabel(self)
        self.cal_read.resize(150,150)
        self.cal_read.setText("0 kcal")
        self.cal_read.setFont(addedfont)
        self.cal_read.move(0.55*self.screen.width(),0.5*self.screen.height())


        # Equation Symbols
        self.product = QtGui.QLabel(self)
        self.product.resize(50,50)
        self.product.setText("*")
        self.product.setFont(readfont)
        self.product.move(0.25*self.screen.width()+10,0.35*self.screen.height())
        
        self.equal = QtGui.QLabel(self)
        self.equal.resize(50,50)
        self.equal.setText("=")
        self.equal.setFont(readfont)
        self.equal.move(0.6*self.screen.width()-15,0.35*self.screen.height())
        
        # Exit button
        self.kill = QtGui.QPushButton("Exit",self)
        self.kill.setFont(self.buttonFont)
        self.kill.clicked.connect(self.kill_press)
        self.kill.resize(100,100)
        self.kill.move(self.screen.width()-280,self.screen.height()-120)
        self.kill.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #00ffda, stop: 1 #00dbde)")
      
        #Power Graph Button (Added by Rosemary Alden)
        self.graph = QtGui.QPushButton("Graph",self)
        self.graph.setFont(addedfont)
        self.graph.clicked.connect(self.graph_press)
        self.graph.resize(100,100)
        self.graph.move(self.screen.width()-150,self.screen.height()-120)
        self.graph.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #00ffda, stop: 1 #00dbde)")    

        # Hold button
        self.hold = QtGui.QPushButton("Hold",self)
        self.hold.setFont(self.buttonFont)
        self.hold.clicked.connect(self.hold_press)
        self.hold.resize(100, 100)
        self.hold.move(150,self.screen.height()-120)
        self.hold.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #00ffda, stop: 1 #00dbde);")
        self.holdFlag = False

        # Resume button
        self.resume = QtGui.QPushButton("Resume",self)
        self.resume.setFont(self.pressedFont)
        self.resume.clicked.connect(self.resume_press)
        self.resume.resize(150,100)
        self.resume.move(300,self.screen.height()-120)
        self.resume.setStyleSheet("background-color:qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #00dbde, stop: 1 #00ffda,);")

        # Set timer interval
        self.timer.start(100)

    def kill_press(self):
        self.kill.setStyleSheet("background-color:qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #00dbde, stop: 1 #00ffda,);")
        sys.exit()

    def hold_press(self):
        if self.holdFlag == False:
            self.hold.setStyleSheet("background-color:qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #00dbde, stop: 1 #00ffda,);")
            self.hold.setFont(self.pressedFont)
            self.resume.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #00ffda, stop: 1 #00dbde);")
            self.resume.setFont(self.buttonFont)
            self.timer.stop()
            self.holdFlag = True
            
    def graph_press(self):
        #print('graph')
        plt.figure(num = 'SPARK Electric Bike' )
        plt.plot([self.tme], [self.pwr], 'bo') #should be blue circles
        #plt.plot([0,1,2], [0,1,2], 'bo') #should be blue circles
        plt.title('Power Generated')
        plt.xlabel('Time (Sec)')
        plt.ylabel('Power (Watts)')
        plt.show()

    def resume_press(self):
        if self.holdFlag == True:
            self.resume.setStyleSheet("background-color:qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #00dbde, stop: 1 #00ffda,);")
            self.resume.setFont(self.pressedFont)
            self.hold.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #00ffda, stop: 1 #00dbde);")
            self.hold.setFont(self.buttonFont)
            self.timer.start(200)
            self.holdFlag = False

    def update_data(self):

        #ser.write("rose")
        ser.flush()
        self.input= ser.readline()
        self.volt_value= self.input.split(' ')[0]
        self.curr_value= self.input.split(' ')[1]
        self.curr_value= self.curr_value.split('\n')[0]
        self.curr_float = float(self.curr_value)
        self.volt_float = float(self.volt_value)
        
        self.power_float = self.volt_float * self.curr_float
        self.power_float = round(self.power_float,3)
        
        self.volt_read.setText(self.volt_value + " V")
        self.curr_read.setText(self.curr_value + " A")        
        self.power_read.setText(str(self.power_float)+ " W")

#Updating Database
    
        point= time.time() - start
        c.execute("""INSERT INTO pedaling (power, time)  VALUES(?,?)""", (self.power_float, point))
        conn.commit()
        
        c.execute("SELECT * FROM pedaling")
        records =c.fetchall()
        self.pwr = []
        for column in records:
            self.pwr.append(column[0])
       

        self.tme = []
        for column in records:
            self.tme.append(column[1])
      

        self.energy = np.trapz( self.pwr, x= self.tme)
        self.energy = self.energy /(60 * 60) #to convert to hours
       
        self.cost_value = self.energy * .0873
        self.cost_value = round(self.cost_value, 4)
        self.cost_read.setText("$" + str( self.cost_value))
       

        ## Calorie calculations (860.421 kcal/ kWh)
        self.cal_value = (self.energy) * 860.421
        self.cal_value = round(self.cal_value, 3)
        self.cal_read.setText( str(self.cal_value) + " kcal")


                           
class OpenWindow(QtGui.QMainWindow):

    def __init__(self):
        super(OpenWindow, self).__init__()
        self.screen = QtGui.QDesktopWidget().screenGeometry()
        self.center = QtGui.QDesktopWidget().screenGeometry().center()
        self.setWindowTitle("SigmaCycle")
        self.setWindowIcon(QtGui.QIcon('/home/pi/Logo.jpg'))
        self.setStyleSheet("background-color: white;")
        self.logo = QtGui.QLabel(self)
        self.pixmap = QtGui.QPixmap("/home/pi/Logo.jpg")
        self.pixmap = self.pixmap.scaledToHeight(self.screen.height()-(self.screen.height()/5))
        self.logo.setPixmap(self.pixmap)
        self.logo.resize(self.pixmap.width(),self.pixmap.height())
        self.logoCenter = self.logo.geometry().center()
        self.logo.move(self.center-self.logoCenter)
        buttonFont = QtGui.QFont("Times",35,QtGui.QFont.Bold)
       
        
        # Start button
        self.start = QtGui.QPushButton("Start",self)
        self.start.setFont(buttonFont)
        self.start.clicked.connect(self.handleStartButton)
        self.dialog = DataWindow()
        self.start.resize(150,150)
        self.start.move(0.08*self.screen.width(),0.35*self.screen.height())
        self.start.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #00ffda, stop: 1 #00dbde);")
        
        # Exit button
        self.kill = QtGui.QPushButton("Exit",self)
        self.kill.setFont(buttonFont)
        self.kill.clicked.connect(self.kill_press)
        self.kill.resize(150,150)
        self.kill.move(0.75*self.screen.width(),0.35*self.screen.height())
        self.kill.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #00ffda, stop: 1 #00dbde);")

        self.showFullScreen()

    def handleStartButton(self):
        self.dialog.showFullScreen()


    def kill_press(self):
        self.kill.setStyleSheet("background-color:qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #00dbde, stop: 1 #00ffda,);")
        sys.exit()


        
def run():
    app = QtGui.QApplication(sys.argv)
    GUI = OpenWindow()
    app.exec_()
    sys.exit(app.exec_())


run()

