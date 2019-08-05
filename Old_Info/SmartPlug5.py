import sys,os
import time
#from scipy.interpolate import interp1d  
#import numpy as np
import sqlite3
#import matplotlib.pyplot as plt
#from scipy import integrate

#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
#from matplotlib.figure import Figure

#import random
import serial
from tkinter import *
import csv



start= time.time()
conn = sqlite3.connect(':memory:')
c = conn.cursor()
c.execute("""CREATE TABLE plugData(current real, voltage real, time real)""")
c.execute("SELECT * FROM plugData WHERE time != 0") #for degugging prints all from database
#print(c.fetchall())
conn.commit()

ser = serial.Serial('/dev/ttyACM0')  # open serial port
ser.baudrate = 115200
ser.flushInput()
#print(ser.name)         # check which port was really used

#c = csv.writer(open("Plug_Data.csv", "wb") )
#c.writerow( ["Time","Current", "Voltage"])

window = Tk()
window.title("Smart Plug")
window.geometry('350x200')

#limit = 10
#period = 1000


def relay_open():
    ser.write(b'0')
    #print('open?')
    
def relay_close():
    ser.write(b'1')
    #print('close?')
    
def update_data():
 i = 0
 j = 0
 ser.flushInput()
 points = 10
 rows_csv = points + 1
 
 data = list()
 data.append(['Time', 'Current', 'Voltage'])

 while i <= points:  #change number to be as large as needed
    if ser.inWaiting()> 0:

        inputString = ser.readline().decode('ascii')

        print(inputString)
       
        timeBoi = str(inputString.split()[0])
        analogBoi = str(inputString.split()[1])
        voltBoi = str(inputString.split()[2])
        
        v_out = (rawValue/1024.00000)*4.8000
        currBoi= 40.0000(v_out - 2.480000)
        currBoi = string(currBoi)
        
        data.append([timeBoi, currBoi, voltBoi])

        print(data)


        #csv_writer.writerow([ timeBoi, currBoi, voltBoi])
        #print('data in')
        
        #print(tme)
        #print(current)
        #print(voltage)

        i = i+1

        #time.sleep(.5) #slows down to try to match the data coming from the arduino
        
    #else:
        #print('No data from Arduino')

    
 with open('Plug_Data.csv', 'wt') as f:
        csv_writer = csv.writer(f)
        
        while j <  rows_csv:  #change number to be one more that i
            csv_writer.writerow(data[j])
            print(data[j])
            j=j+1
   

relay1 = Button(window, text = "Relay Open", command = relay_open)
relay1.grid(column=0, row = 0)

relay2 = Button(window, text = "Relay Close", command = relay_close)
relay2.grid(column=1, row =0)

dataCollect = Button(window, text = "Collect Data", command = update_data)
dataCollect.grid(column=2, row = 0)



window.mainloop()













