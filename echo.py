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
from datetime import datetime
from remote_storage import GoogleDrive
from echo_logger import Logger

### CONSTANTS ###
VIDEO_FILE_TYPES = (".mp4", ".mov", ".avi")
DATA_FILE_TYPES = (".csv")
APP_START_TIME = int(round(time.time() * 1000))

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

def print_help():
    """
    Prints the help text to terminal (invoked by adding the -h flag)
    """
    print("BURPG Echo\n"
          "Usage: " + os.path.basename(__file__) + " -p search_path [-ahilv] [-s secret_path] [-c credentials_path]\n"
          "\n"
          "See README.md for command line help")


# Handle Command Line Options
try:
    opts, args = getopt.getopt(sys.argv[1:], "hlaivp:s:c:n", [
        "help", "log", "automatic", "interactive", "verbose", "path=",
        "secret=", "credentials=", "noauth_local_webserver"])
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

# Create Logger and Write Initial logs
if log_path is not None and not os.access(os.path.dirname(log_path), os.W_OK):
    print("ERROR: Unable to write to log. Check permissions.")
    sys.exit(2)

logger = Logger(verbose_mode, log_path)
logger.log_verbose("Echo Session Begin")
logger.log_verbose("Log File: " + str(log_path))
logger.log_verbose("Interactive Mode: " + str(interactive_mode))
logger.log_verbose("Search Directory: " + str(search_path))
logger.log_verbose("API Client Secret File: " + str(secret_path))
logger.log_verbose("Credentials File: " + str(credentials_path))

# Sanity Checks
if search_path is None:
    logger.log("ERROR: Must specify search directory path.")
    print_help()
    sys.exit(2)
if not os.path.isdir(search_path) or not os.access(search_path, os.R_OK):
    logger.log("ERROR: " + search_path + " does not exist, is not a directory, or is not readable.")
    print_help()
    sys.exit(2)
if secret_path is None:
    logger.log_verbose("No API client secret file specified. Using " +
                       os.getcwd() + "/client_secrets.json.")
    secret_path = os.getcwd() + "/client_secrets.json"
if not os.path.isfile(secret_path) or not os.access(secret_path, os.R_OK):
    logger.log("ERROR: " + secret_path + " does not exist, is not a file, or is not readable.")
    print_help()
    sys.exit(2)
if credentials_path is None:
    logger.log_verbose("No credentials file specified. Using " +
                       os.getcwd() + "/drive.credentials.")
    credentials_path = os.getcwd() + "/drive.credentials"

logger.log_verbose("Initialization complete. Welcome to BURPG Echo.")


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
                logger.log_verbose("Found data file: " + os.path.join(subdir, file))
    return output_list

# Locate Files of Interest
data_list = find_data(search_path)
video_list = find_videos(search_path)

# Create Google Drive connection (will prompt for user login if necessary)
drive = GoogleDrive(logger, secret_path=secret_path,
                    credentials_path=credentials_path,
                    noauth_local_webserver=noauth_local_webserver)

# Upload Data Files
if len(data_list) is not 0:
    logger.log("Beginng Data File Upload...")
    folder_id = drive.create_folder("EchoData-" + datetime.utcnow().strftime("%Y.%m.%d.%H%M"))
    for data_file in data_list:
        drive.upload_file(data_file, folder_id)
    logger.log("All data files uploaded.")
else:
    logger.log("No data files found. Skipping upload.")

# Upload Video Files
if len(video_list) is not 0:
    logger.log("Beginng Video File Upload...")
    folder_id = drive.create_folder("EchoVideo-" + datetime.utcnow().strftime("%Y.%m.%d.%H%M"))
    for video_file in video_list:
        drive.upload_file(video_file, folder_id)
    logger.log("All video files uploaded.")
else:
    logger.log("No video files found. Skipping upload.")

# All Done!
logger.log("All operations completed after " +
           str(int(round(time.time() * 1000)) - APP_START_TIME) + "ms. Goodbye.")
