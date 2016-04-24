# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 21:03:14 2016

@author: silvia_zhang_97
"""
import matplotlib.pyplot as plt
from scipy import signal
class DataAnalysis:
    
    def __init__(self,interactive):
        interactive = False
    
    def simple_plot(title,x,y,xlabel,ylabel):
        """
         plots single telemetry value over time 
         :param title: title of the plot
         :param x: list of regularly incremented time values
         :param y: list of telemetry values per x value
         :param xlabel: x variable name and units ie. Time(s)
         :param ylabel: y variable name and units ie. Thrust(lbs)
        """
        plt.figure();
        plt.plot(x,y);
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
    
    
    def filter_data(y,N,Wn):
        """
        takes raw telemetry data and applies a butterworth filter
        :param y: raw telemetry data
        :param N: order of butterworth filter
        :param Wn: cutoff frequency
        """
        b,a, = signal.butter(N,Wn, output = 'ba')
        yf = signal.filtfilt(b,a, y)
        return yf
        
