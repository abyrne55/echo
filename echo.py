#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103
"""
Boston University Rocket Propulsion Group: Echo
Post-Rocket Engine Test Data Upload & Analysis Tool
Created by Anthony Byrne & Silvia Zhang for ENG EK128 (Spring 2016)

See LICENSE for MIT/X11 license info.
See README.md for all other help.
"""

### IMPORTS ###
import getopt
import sys
import os
import time
from remote_storage import RemoteStorage as rs

### CONSTANTS ###
VIDEO_FILE_TYPES = (".mp4", ".mov", ".avi")
DATA_FILE_TYPES = (".csv")

### GLOBALS ###
# Interactive Mode: shows graph in pop-up windows without saving them to file
interactive_mode = False
# Verbose Mode: log everything to console
verbose_mode = False
# Log Path: log all messages to a file if set
log_path = None
# Search Path: the folder to search for relevant files in (videos, CSV's, etc.)
search_path = None
# Secret Path: the path to the file that contains our Google Drive login info.
# If not set, defaults to looking for a file named 'drive.secret' at the top of
# the search_path
secret_path = None

### HELPER METHODS ###


def print_help():
    """
    Prints the help text to terminal (invoked by adding the -h flag)
    """
    print("BURPG Echo\n"
          "TODO: Add help text\n")


def log(message):
    """
    Logs a message to the console and (if log_path is set) a file

    :param message: the message to be logged
    """
    print(message)
    if log_path != None:
        with open("echo.log", "a") as logfile:
            logfile.write("[" + str(int(time.time())) + "] " + message + "\n")


def log_verbose(message):
    """
    Logs a message to the console and (if log_path is set) a file, but only if
    verbose_mode is enabled

    :param message: the verbose message to be logged
    """
    if verbose_mode:
        log(message)


# Handle Command Line Options
try:
    opts, args = getopt.getopt(sys.argv[1:], "hlaivp:s:", [
        "help", "log", "automatic", "interactive", "verbose", "path=", "secret="])
except getopt.GetoptError:
    print("Invalid Argument")
    print_help()
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print_help()
        sys.exit()
    elif opt in ("-l", "--log"):
        log_path = os.getcwd() + "/echo.log"
        log_verbose("Logging to " + os.getcwd() + "/echo.log")
    elif opt in ("-v", "--verbose"):
        verbose_mode = True
        log_verbose("Entering Verbose Mode")
    elif opt in ("-a", "--automatic"):
        interactive_mode = False
        log_verbose("Entering Automatic Mode")
    elif opt in ("-i", "--interactive"):
        interactive_mode = True
        log_verbose("Entering Interactive Mode")
    elif opt in ("-p", "--path"):
        search_path = os.path.realpath(arg)
        log_verbose("Will search for files of interest in " + search_path)
    elif opt in ("-s", "--secret"):
        secret_path = os.path.realpath(arg)
        log_verbose("Will use Google Drive authentication details in " + secret_path)

# Sanity Checks
if log_path is not None and not os.access(os.path.dirname(log_path), os.W_OK):
    print("ERROR: Unable to write to log. Check permissions.")
    sys.exit(2)
if search_path is None:
    log("ERROR: Must specify search directory path.")
    print_help()
    sys.exit(2)
if not os.path.isdir(search_path) or not os.access(search_path, os.R_OK):
    log("ERROR: " + search_path + " does not exist, is not a directory, or is not readable.")
    print_help()
    sys.exit(2)
if secret_path is None:
    log_verbose("No search directory specified. Using " + search_path + "/drive.secret.")
    secret_path = search_path + "/drive.secret"
if not os.path.isfile(secret_path) or not os.access(secret_path, os.R_OK):
    log("ERROR: " + secret_path + " does not exist, is not a file, or is not readable.")
    print_help()
    sys.exit(2)

log_verbose("Welcome to BURPG Echo.")


def find_videos(path):
    """
    Search the given path recursively and return a list of video files

    :param path: the path to search
    :returns: a list of video file path strings
    """
    # "Walk" through the files in the search dir and check for video file extensions
    output_list = list()
    for subdir, dirs, files in os.walk(path):
        del dirs
        for file in files:
            if file.lower().endswith(VIDEO_FILE_TYPES):
                output_list.append(os.path.join(subdir, file))
    return output_list

def find_data(path):
    """
    Search the given path recursively and return a list of telemetry data files

    :param path: the path to search
    :returns: a list of data file path strings
    """
    # "Walk" through the files in the search dir and check for video file extensions
    output_list = list()
    for subdir, dirs, files in os.walk(path):
        del dirs
        for file in files:
            if file.lower().endswith(DATA_FILE_TYPES):
                output_list.append(os.path.join(subdir, file))
    return output_list

data_list = find_data(search_path)
print(data_list)
my_rs = rs()
print(my_rs.upload_file(data_list[0]))
# csv_files = locate_csv_files()
# video_files = locate_video_files()
