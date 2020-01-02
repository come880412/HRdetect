import matplotlib.pyplot as plt
import numpy as np
import time
import time
import random
import math
import serial
from collections import deque
from scipy import signal


#Display loading
class PlotData:
    def __init__(self, max_entries=30):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)

    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)

#存時間差
class time_Data: 
    def __init__(self, max_entries=30):
        self.time = deque(maxlen=max_entries)

    def add(self, y):
        self.time.append(y)


fs = 100 #取樣頻率
j = (-1)**(1/2) #虛數
#畫圓
angle = np.linspace(-np.pi, np.pi, 50)  # 創建等差數列 ，-pi~pi之間建立50個等差數列
cirx = np.sin(angle)
ciry = np.cos(angle)
#算Z-domain的根
coe = np.array([1/5, 1/5, 1/5, 1/5, 1/5])
#coe = np.array([1/6,1/6, 1/6, 1/6, 1/6, 1/6])
H = np.roots(coe)
#Z-domain plot
plt.figure(figsize=(8, 8))
plt.title('Filter Z-Plot')
plt.xlim((-2, 2))
plt.xlabel('Real')
plt.ylim((-2, 2))
plt.ylabel('Imag')
plt.plot(cirx, ciry, 'k-')
plt.plot(np.real(H), np.imag(H), 'o', markersize=12)
plt.plot(0, 0, 'x', markersize=12)
plt.grid()

#initial
fig, (ax, ax2, ax3, ax4) = plt.subplots(4, 1)
line,  = ax.plot(np.random.randn(100))
line2, = ax2.plot(np.random.randn(100))
line3, = ax3.plot(np.random.randn(100))
line4, = ax4.plot(np.random.randn(100))
plt.show(block=False)
plt.setp(line2, color='r')


PData = PlotData(500)
ax.set_ylim(-5, 7)
ax2.set_ylim(-5, 7)
ax3.set_ylim(0, 50)
ax4.set_ylim(0, 50)

ax3.set_xlim(0, fs)
ax4.set_xlim(0, fs)


# plot parameters
print('plotting data...')
# open serial port
strPort = 'com5'
ser = serial.Serial(strPort, 115200)
ser.flush()
timed = time_Data(max_entries=200)
start = time.time()
temp = deque(maxlen=20)

temp_HR = deque(maxlen=100)

while True:
#for iii in range(400):
    for ii in range(10):

        try:
            data = float(ser.readline())
            temp.append(data)
            PData.add(time.time() - start, data-np.mean(temp))
        except:
            pass

    PData_filter = signal.lfilter(coe, 1, PData.axis_y)
    PData_F = np.fft.fft(PData.axis_y)
    PData_filter_F = np.fft.fft(PData_filter)
#HR & HRV
    if len(PData_filter)>150:
        PData_filter_array=np.array(PData_filter)
        m1=np.argmax(PData_filter_array[:70])
        m2=np.argmax(PData_filter_array[70:150])+70
        if PData_filter[m1] < 0.8 or PData_filter[m2] < 0.8:
            plt.xlabel('HR: No' + '  HRV: '+ str(round(np.std(timed.time),3)))
        elif PData_filter[m1] > 10 or PData_filter[m2] > 10:
            plt.xlabel('HR: No' + '  HRV: '+ str(round(np.std(timed.time),3)))
        elif m2-m1>=50:
            HR=int(1/(m2-m1)*fs*60) 
            if  HR > np.mean(temp_HR)-20 or HR < np.mean(temp_HR)+20:    
            #if  HR > 50 and HR < 120:      
                temp_HR.append(HR)
                timed.add(round((m2-m1)/fs,4))
                plt.xlabel('HR: '+ str(HR) + '  HRV: ' + str(round(np.std(timed.time),3)))

    ax.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
    ax2.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)

    line.set_xdata(PData.axis_x)
    line.set_ydata(PData.axis_y)

    line2.set_xdata(PData.axis_x)
    line2.set_ydata(PData_filter)

    hz = np.arange(0, fs, fs/len(PData_F))

    line3.set_ydata(PData_F)
    line3.set_xdata(hz[:len(PData_F)])

    line4.set_ydata(PData_filter_F)
    line4.set_xdata(hz[:len(PData_filter_F)])

    fig.canvas.draw()
    fig.canvas.flush_events()

print('HR_Num: ' + str(len(temp_HR)))
print('HR_Mean: '+ str(int(np.mean(temp_HR))))
print('HR_Max: ' + str(np.max(temp_HR)))
print('HR_Min: ' + str(np.min(temp_HR)))
print('HR_Std: ' + str(round(np.std(temp_HR),3)))

