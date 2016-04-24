# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from scipy import signal
import os 
class DataAnalysis:
    interactive = False
    LINE_COLORS = ["#de3c80","#d9013a","#d47e20","#17c009","#196512","#2a9e60","#116186"]
    def __init__(self,interactive, location = os.getcwd()):
        self.interactive = interactive
        
    
    def plotit(self,data,title,xlabel,ylabel):
        """
         plots telemetry values given in a list
        
         if there are multiple telemetry values, they will be in a list of lists
         This method will work for a single or multiple plots.
         if interactive is true, will print plot to screen as a figure
         else, it will save the figure as a pdf using the title found in the dataset
         
         :param data: Either a DataSet object or a list of DataSet Objects
         :param title: Title of the plot
         :param xlabel: label on x axis in form "Type (units)" ie. "Time (s)"
         :param ylabel: label on y axis in form "Type (units)" ie. "Thrust (lbs)"
        """
        legendnames = []
        dslist = []
        
        if (len(data) > 1):
            dslist = data
    
        else:
            dslist = [data]
        for ds in dslist:
            plt.plot(ds.xlist,ds.ylist, color = DataAnalysis.LINE_COLORS[dslist.index(ds)])
            legendnames.append(ds.dataname)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
                
        
        if (self.interactive == True):
            plt.show()
        else:
            plt.savefig(ds.title + ".pdf")
        
            
    def filter_data(self,y,N,Wn):
        """
        takes raw telemetry data and applies a butterworth filter
        
        :param y: raw telemetry data
        :param N: order of butterworth filter
        :param Wn: cutoff frequency
        :returns: filtered data
        """
        b,a, = signal.butter(N,Wn, output = 'ba')
        yf = signal.filtfilt(b,a, y)
        return yf
        
            
