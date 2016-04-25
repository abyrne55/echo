# -*- coding: utf-8 -*-
# pylint: disable-msg=R0201, R0903
"""
BURPG Echo
See LICENSE for MIT/X11 license info.
See README.md for all other help.
"""

import matplotlib.pyplot as plt
from scipy import signal


class DataAnalysis:
    """
    DataAnalysis provides plotting and filtering functionality for raw telemetry
    data.
    """
    interactive = False
    LINE_COLORS = ["#de3c80", "#d9013a", "#d47e20", "#17c009", "#196512", "#2a9e60", "#116186"]

    def __init__(self, interactive):
        self.interactive = interactive

    def plot_dataset(self, data, title, xlabel, ylabel):
        """
         Plots telemetry values given in a list.

         If there are multiple telemetry values, they will be in a list of lists
         This method will work for a single or multiple plots.
         If interactive is true, will print plot to screen as a figure otherwise
         it will save the figure as a pdf using the title found in the dataset

         :param data: Either a DataSet object or a list of DataSet Objects
         :param title: Title of the plot
         :param xlabel: label on x axis in form "Type (units)" ie. "Time (s)"
         :param ylabel: label on y axis in form "Type (units)" ie. "Thrust (lbs)"
        """
        legendnames = []
        dslist = []

        if len(data) > 1:
            dslist = data
        else:
            dslist = [data]

        for dataset in dslist:
            plt.plot(dataset.xlist, dataset.ylist,
                     color=DataAnalysis.LINE_COLORS[dslist.index(dataset)])
            legendnames.append(dataset.dataname)
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)

            if self.interactive:
                plt.show()
            else:
                plt.savefig(dataset.title + ".pdf")

    def filter_data(self, raw, order, cutoff):
        """
        Takes raw telemetry data and applies a Butterworth filter

        :param raw: raw telemetry data
        :param order: order of butterworth filter
        :param cutoff: cutoff frequency
        :returns: filtered data
        """
        numerator, denominator = signal.butter(order, cutoff, output='ba')
        return signal.filtfilt(numerator, denominator, raw)


class DataSet:
    """
    Datasets store lists of data points and a title, to make plotting easier
    """

    def __init__(self, dataname, xlist, ylist):
        """
        Constructor

        :param dataname: telemetry value being plotted ie VOXB
        :param xlist: list of independent values to be plotted over
        :param ylist: list of telemetry values to plot over xlist
        """
        self.dataname = dataname
        self.xlist = xlist
        self.ylist = ylist
