# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103
"""
BURPG Echo
See LICENSE for MIT/X11 license info.
See README.md for all other help.
"""
import time


class Logger:
    """
    Provides a logging "singleton" instance that can be passed around as needed
    """

    LOG_PATH = None
    VERBOSE_MODE = False

    def __init__(self, verbose=False, path=None):
        self.VERBOSE_MODE = verbose
        self.LOG_PATH = path

    def log(self, message):
        """
        Logs a message to the console and (if log_path is set) a file

        :param message: the message to be logged
        """
        print(message)
        if self.LOG_PATH != None:
            with open(self.LOG_PATH, "a") as logfile:
                logfile.write("[" + str(int(time.time())) + "] " + message + "\n")

    def log_verbose(self, message):
        """
        Logs a message to the console and (if log_path is set) a file, but only if
        verbose_mode is enabled

        :param message: the verbose message to be logged
        """
        if self.VERBOSE_MODE:
            self.log(message)
