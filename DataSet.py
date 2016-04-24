# -*- coding: utf-8 -*-
"""
Created on Sat Apr 23 02:26:51 2016

@author: silvia_zhang_97
"""

class DataSet:
    def __init__(self, dataname,xlist,ylist):
        """
        A class to create object Datasets to be used for plotting. A list of these are generated, and cannot exceed 10 plots.
        :param dataname: telemetry value being plotted ie VOXB
        :param xlist: list of independent values to be plotted over
        :param ylist: list of telemetry values to plot over xlist
        
        """
        self.dataname = dataname
        self.xlist = xlist
        self.ylist = ylist
        