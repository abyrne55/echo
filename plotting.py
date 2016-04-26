# -*- coding: utf-8 -*-
# pylint: disable-msg=R0201, R0903
"""
BURPG Echo
See LICENSE for MIT/X11 license info.
See README.md for all other help.
"""

import matplotlib.pyplot as plt
from scipy import signal
import numpy as np


class DataAnalysis:
    """
    DataAnalysis provides plotting and filtering functionality for raw telemetry
    data.
    """
    interactive = False
    save_location = "."
    logger = None
    LINE_COLORS = ["#de3c80", "#d9013a", "#d47e20", "#17c009", "#196512", "#2a9e60", "#116186"]

    def __init__(self, logger, interactive, save_location="."):
        self.interactive = interactive
        self.save_location = save_location
        self.logger = logger

    def plot_dataset(self, data, xlabel, ylabel, title=None):
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

        if isinstance(data, list):
            dslist = data
        else:
            dslist = [data]

        for dataset in dslist:
            plt.plot(dataset.xlist, dataset.ylist,
                     color=DataAnalysis.LINE_COLORS[dslist.index(dataset)])
            legendnames.append(dataset.dataname)

            if title is None:
                plt.title(dataset.dataname)
            else:
                plt.title(title)

            plt.xlabel(xlabel)
            plt.ylabel(ylabel)

            if self.interactive:
                plt.show()
            else:

                plt.savefig(self.save_location + "/" +
                            dataset.dataname + ".pdf", bbox_inches='tight')

    def butter_filter_data(self, raw, order, cutoff):
        """
        Takes raw telemetry data and applies a Butterworth filter

        :param raw: an array of raw telemetry data
        :param order: order of butterworth filter
        :param cutoff: cutoff frequency
        :returns: filtered data
        """
        numerator, denominator = signal.butter(order, cutoff, output='ba')
        return signal.filtfilt(numerator, denominator, raw)

    def moving_average_filter_data(self, raw, interval):
        """
        Takes raw telemetry data and applies a moving average filter
        Citation: Based on this StackOverflow answer: http://stackoverflow.com/a/14314054

        :param raw: an array of raw telemetry data
        :param period: the smoothing interval
        """
        ret = np.cumsum(raw, dtype=float)
        ret[interval:] = ret[interval:] - ret[:-interval]
        return ret[interval - 1:] / interval


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
