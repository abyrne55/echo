#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103,C0413,E0611,W0603
"""
Boston University Rocket Propulsion Group: Echo
Post-Rocket Engine Test Data Upload & Analysis Tool
Created by Anthony Byrne & Silvia Zhang for ENG EK128 (Spring 2016)

See LICENSE for MIT/X11 license info.
See README.md for all other help.
"""

### IMPORTS ###
import time
APP_START_TIME = int(round(time.time() * 1000))
import getopt
import sys
import os
from datetime import datetime
#import numpy as np
from numpy import genfromtxt, dtype, array
from remote_storage import GoogleDrive
from echo_logger import Logger

### CONSTANTS ###
VIDEO_FILE_TYPES = (".mp4", ".mov", ".avi")
DATA_FILE_TYPES = (".csv")
PLOT_FILE_TYPES = (".pdf")

### GLOBALS ###
# Interactive Mode: shows graph in pop-up windows without saving them to file
interactive_mode = False
# Verbose Mode: log everything to console
verbose_mode = False
# Log Path: log all messages to a file if set
log_path = None
# Search Path: the folder to search for relevant files in (videos, CSV's, etc.)
search_path = None
# Client Secret Path: the path to the file that contains our Google Drive API
# info. If not set, defaults to looking for a file named 'client_secrets.json'
# within the current working directory
secret_path = None
# Credentials Path: the path to the file that contains Google user credentials
# (obtained by completing the user authentication flow on first run). If not
# set, we first check the current working directory for 'drive.credentials'. If
# 'drive.credentials' does not exist or is expired, the user auth flow will be
# initiated
credentials_path = None
# noauth_local_webserver. Command line argument passthru to the OAuth2 flow.
noauth_local_webserver = False
# Offline mode. Do everything except for drive upload
offline = False
# T0 time. Correct graphs so that they center correctly on a T0
t_zero = 0.0
override_t_zero = False
# Trim interval. Discard all data this amount of time before and after T0
trim_interval = None


def print_help():
    """
    Prints the help text to terminal (invoked by adding the -h flag)
    """
    print("BURPG Echo\n"
          "Usage: " + os.path.basename(__file__) +
          " -p search_path [-ahilnovz] [-s secret_path] [-c credentials_path]\n"
          "\n"
          "See README.md for command line help")


# Handle Command Line Options
try:
    opts, args = getopt.getopt(sys.argv[1:], "hlaivp:s:c:noz:t:", [
        "help", "log", "automatic", "interactive", "verbose", "path=",
        "secret=", "credentials=", "noauth_local_webserver", "offline", "t_zero=", "trim="])
except getopt.GetoptError:
    print("Invalid Argument")
    print_help()
    sys.exit(2)
# Loop through the argument list given to us by Getopt and process appropriately
# See Globals section above and the README for more information about options
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print_help()
        sys.exit()
    elif opt in ("-l", "--log"):
        log_path = os.getcwd() + "/echo.log"
    elif opt in ("-v", "--verbose"):
        verbose_mode = True
    elif opt in ("-a", "--automatic"):
        interactive_mode = False
    elif opt in ("-i", "--interactive"):
        interactive_mode = True
    elif opt in ("-p", "--path"):
        search_path = os.path.realpath(arg)
    elif opt in ("-s", "--secret"):
        secret_path = os.path.realpath(arg)
    elif opt in ("-c", "--credentials"):
        credentials_path = os.path.realpath(arg)
    elif opt in ("-n", "--noauth_local_webserver"):
        noauth_local_webserver = True
    elif opt in ("-o", "--offline"):
        offline = True
    elif opt in ("-z", "--t_zero"):
        override_t_zero = True
        t_zero = float(arg)
    elif opt in ("-t", "--trim"):
        trim_interval = float(arg)

# Create Logger and Write Initial logs
if log_path is not None and not os.access(os.path.dirname(log_path), os.W_OK):
    print("ERROR: Unable to write to log. Check permissions.")
    sys.exit(2)

# Log some key information for debugging purposes
logger = Logger(verbose_mode, log_path)
logger.log_verbose("Echo Session Begin")
logger.log_verbose("Log File: " + str(log_path))
logger.log_verbose("Interactive Mode: " + str(interactive_mode))
logger.log_verbose("Search Directory: " + str(search_path))
logger.log_verbose("API Client Secret File: " + str(secret_path))
logger.log_verbose("Credentials File: " + str(credentials_path))
logger.log_verbose("Offline: " + str(offline))
logger.log_verbose("T0 Time: " + str(t_zero))
logger.log_verbose("Trim Interval: " + str(trim_interval))

# Sanity Checks
# Check if a search path was specified
if search_path is None:
    logger.log("ERROR: Must specify search directory path.")
    print_help()
    sys.exit(2)
# Check if we can access the search path with read permissions
if not os.path.isdir(search_path) or not os.access(search_path, os.R_OK):
    logger.log("ERROR: " + search_path + " does not exist, is not a directory, or is not readable.")
    print_help()
    sys.exit(2)
# Only perform the following checks if we plan to upload to Google Drive
if not offline:
    # Check the "client secret" path
    if secret_path is None:
        logger.log_verbose("No API client secret file specified. Using " +
                           os.getcwd() + "/client_secrets.json.")
        secret_path = os.getcwd() + "/client_secrets.json"
    # Check that we can access the client secret
    if not os.path.isfile(secret_path) or not os.access(secret_path, os.R_OK):
        logger.log("ERROR: " + secret_path + " does not exist, is not a file, or is not readable.")
        print_help()
        sys.exit(2)
    # Try to load a credentials file (not really required, since the user can
    # just complete the Google authentication flow to get a new one
    if credentials_path is None:
        logger.log_verbose("No credentials file specified. Using " +
                           os.getcwd() + "/drive.credentials.")
        credentials_path = os.getcwd() + "/drive.credentials"

logger.log_verbose("Initialization complete. Welcome to BURPG Echo.")


def csv_to_array(path):
    """
    Read a CSV file into a NumPy array, while ensuring that the resulting array is 2D

    :param path: path to CSV file
    :returns: the resulting NumPy array
    """
    arr = genfromtxt(path, delimiter=",", dtype=dtype(float))
    # Ensure the array is 2D (since genfromtxt() reads a 1 line CSV as a 1D array)
    if len(arr.shape) is 1:
        arr = array([array([0, 0]), arr])
    return arr


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
                logger.log_verbose("Found video file: " + os.path.join(subdir, file))
    return output_list


def find_data(path):
    """
    Search the given path recursively and return a list of telemetry data files.
    Also looks for a "t0_time.csv" file to set the t_zero gloabl variable.

    :param path: the path to search
    :returns: a list of data file path strings
    """
    # "Walk" through the files in the search dir and check for data file extensions
    output_list = list()
    for subdir, dirs, files in os.walk(path):
        del dirs
        for file in files:
            if file.lower().endswith(DATA_FILE_TYPES) and not file.lower().endswith("t0_time.csv"):
                output_list.append(os.path.join(subdir, file))
                logger.log_verbose("Found data file: " + os.path.join(subdir, file))
            # Look for the T0 file
            if not override_t_zero and file.lower().endswith("t0_time.csv"):
                t0_arr = csv_to_array(os.path.join(subdir, file))
                for row in t0_arr:
                    if row[1] > 0:
                        global t_zero
                        t_zero = float(row[0])
                logger.log_verbose("Found new T0 time from file: " + str(t_zero))
    return output_list

# Locate Files of Interest
data_list = find_data(search_path)
video_list = find_videos(search_path)

# Create Google Drive connection (will prompt for user login if necessary)
if not offline:
    drive = GoogleDrive(logger, secret_path=secret_path,
                        credentials_path=credentials_path,
                        noauth_local_webserver=noauth_local_webserver)

# Upload Data Files (if applicable)
if not offline and len(data_list) is not 0:
    logger.log("Beginning Data File Upload...")
    folder_id = drive.create_folder("EchoData-" + datetime.utcnow().strftime("%Y.%m.%d.%H%M"))
    for data_file in data_list:
        drive.upload_file(data_file, folder_id)
    logger.log("All data files uploaded.")
else:
    logger.log("Offline, or no data files found. Skipping upload.")

# Upload Video Files (if applicable)
if not offline and len(video_list) is not 0:
    logger.log("Beginning Video File Upload...")
    folder_id = drive.create_folder("EchoVideo-" + datetime.utcnow().strftime("%Y.%m.%d.%H%M"))
    for video_file in video_list:
        drive.upload_file(video_file, folder_id)
    logger.log("All video files uploaded.")
else:
    logger.log("Offline, or no video files found. Skipping upload.")

# Generate Data Plots
folder_name = "EchoPlots-" + datetime.utcnow().strftime("%Y.%m.%d.%H%M")
plot_list = []
if len(data_list) is not 0:
    logger.log("Beginning Plot Generation...")
    import plotting
    # Ensure our plots folder exists
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    # Create a DataAnalysis object
    analysis = plotting.DataAnalysis(logger, interactive_mode, folder_name)
    # Loop through the data files and plot them, recording plot paths as we go
    for data_file in data_list:
        raw_data_array = csv_to_array(data_file)
        dataset = plotting.DataSet(os.path.basename(
            data_file)[:-4], raw_data_array[:, 0], raw_data_array[:, 1])
        dataset.set_t0(t_zero)
        if trim_interval is None:
            plot_list.append(analysis.plot_dataset(dataset, xlabel="Time (s)",
                                                   ylabel="Units"))
        else:
            plot_list.append(analysis.plot_dataset(dataset, xlabel="Time (s)",
                                                   ylabel="Units",
                                                   xlimits=(-trim_interval, trim_interval)))

    ## Filtered multiplot test code ##
    multilist = []

    # Run the first dataset through a 5th order Butterworth filter
    filtered_data = analysis.butter_filter_data(raw_data_array[:, 1], 5, 2/150/2)
    raw_data_array = csv_to_array(data_list[0])

    # Create a new DataSet object based on the filtered data
    multilist.append(plotting.DataSet(os.path.basename(
        data_list[0])[:-4], raw_data_array[:, 0], filtered_data))
    multilist[0].set_t0(t_zero)

    # Run the second dataset through a 5th order Butterworth filter
    raw_data_array = csv_to_array(data_list[1])
    filtered_data = analysis.butter_filter_data(raw_data_array[:, 1], 5, 2/150/2)

    # Create a new DataSet object based on the filtered data
    multilist.append(plotting.DataSet(os.path.basename(
        data_list[1])[:-4], raw_data_array[:, 0], filtered_data))
    multilist[1].set_t0(t_zero)
    plot_list.append(analysis.plot_dataset(multilist, xlabel="Time (s)", ylabel="Units"))


# Upload Plots (if applicable)
if not offline and len(plot_list) is not 0:
    logger.log("Beginning Plot File Upload...")
    folder_id = drive.create_folder("EchoPlots-" + datetime.utcnow().strftime("%Y.%m.%d.%H%M"))
    for plot_file in plot_list:
        drive.upload_file(plot_file, folder_id)
    logger.log("All plot files uploaded.")
else:
    logger.log("Offline, or no plot files found. Skipping upload.")

# All Done!
logger.log("All operations completed after " +
           str(int(round(time.time() * 1000)) - APP_START_TIME) + "ms. Goodbye.")
