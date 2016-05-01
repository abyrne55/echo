# -*- coding: utf-8 -*-
# pylint: disable-msg=R0201,R0903,E1101,R0913
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
    save_folder = "."
    logger = None
    LINE_COLORS = ["#de3c80", "#196512", "#d47e20", "#17c009", "#d9013a", "#2a9e60", "#116186"]

    def __init__(self, logger, interactive, save_folder="."):
        self.interactive = interactive
        self.save_folder = save_folder
        self.logger = logger

    def plot_dataset(self, data, xlabel, ylabel, title=None, xlimits=None):
        """
         Plots telemetry values given in a list.

         If there are multiple telemetry values, they will be in a list of lists
         This method will work for a single or multiple plots.
         If interactive is true, will print plot to screen as a figure otherwise
         it will save the figure as a pdf using the title found in the dataset

         :param data: Either a DataSet object or a list of DataSet Objects
         :param xlabel: label on x axis in form "Type (units)" ie. "Time (s)"
         :param ylabel: label on y axis in form "Type (units)" ie. "Thrust (lbs)"
         :param title: Title of the plot
         :param xlimits: a tuple containing the x limits ie. (-10, 10)
         :returns: path to plot image folder
        """
        legendnames = []
        dslist = []
        dsnamelist = []

        if isinstance(data, list):
            dslist = data
        else:
            dslist = [data]

        for dataset in dslist:
            plt.plot(dataset.xlist, dataset.ylist,
                     color=DataAnalysis.LINE_COLORS[dslist.index(dataset)])
            legendnames.append(dataset.dataname)
            dsnamelist.append(dataset.dataname)

        save_path = ""
        if title is None:
            if len(dslist) > 1:
                plt.title(" vs. ".join(dsnamelist))
                save_path = self.save_folder + "/" + "_vs_".join(dsnamelist) + ".pdf"
            else:
                plt.title(dslist[0])
                save_path = self.save_folder + "/" + dslist[0].dataname + ".pdf"
        else:
            plt.title(title)
            save_path = self.save_folder + "/" + title + ".pdf"

        if len(dslist) > 1:
            plt.legend(legendnames, loc="upper right")

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        axis = plt.gca()
        axis.grid(which='minor', alpha=0.2)
        axis.grid(which='major', alpha=0.5)
        #plt.yticks(np.arange(min(dslist[0].ylist), max(x)+1, 1.0))

        if xlimits is not None:
            axis.set_xlim(xlimits[0], xlimits[1])

        if self.interactive:
            plt.show()

        plt.savefig(save_path, bbox_inches='tight')
        self.logger.log_verbose("Generated Graph " + save_path)
        plt.close()
        return save_path

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
    t0_time = 0

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

    def __str__(self):
        return self.dataname

    def set_t0(self, t0_time):
        """
        Adjust the x-values for a given t0 time

        :param t0_time: the desired t0 time
        """
        self.t0_time = t0_time

        for x_index, x_value in enumerate(self.xlist):
            self.xlist[x_index] = float(x_value) - float(t0_time)
