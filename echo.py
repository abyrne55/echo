"""
Boston University Rocket Propulsion Group: Echo
Post-Rocket Engine Test Data Upload & Analysis Tool
Created by Anthony Byrne & Silvia Zhang for ENG EK128 (Spring 2016)

See LICENSE for MIT/X11 license info.
See README.md for all other help.
"""

# Imports
import getopt, sys, os, time

# Interactive Mode: shows graph in pop-up windows without saving them to file
interactive_mode = False
# Verbose Mode: log everything to console
verbose_mode = False
# Log Path: log everything to a file if set
log_path = None
# Search Path: the folder to search for relevant files in (videos, CSV's, etc.)
search_path = None
# Secret Path: the path to the file that contains our Google Drive login info.
# If not set, defaults to looking for a file named 'drive.secret' at the top of
# the search_path
secret_path = None

# Initial Methods
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
    if (log_path != None):
        with open("echo.log", "a") as logfile:
            logfile.write("["+str(int(time.time()))+"] "+message+"\n")
            print()
    print("test")
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
    opts, args = getopt.getopt(sys.argv[1:], "hlaivp:s:", ["help", "log", "automatic", "interactive", "verbose", "path=", "secret="])
except getopt.GetoptError:
        print("Invalid Argument")
        print_help()
        sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print_help()
        sys.exit()
    elif opt in ("-l", "--log"):
        log_path = os.getcwd()+"/echo.log"
        print("Logging to "+os.getcwd()+"/echo.log")
    elif opt in ("-v", "--verbose"):
        print("Entering Verbose Mode")
        interactive_mode = True
    elif opt in ("-a", "--automatic"):
        print("Entering Automatic Mode")
        interactive_mode = False
    elif opt in ("-i", "--interactive"):
        print("Entering Interactive Mode")
        interactive_mode = True
    elif opt in ("-p", "--path"):
        search_path = os.path.realpath(arg)
        print("Will search for files of interest in " + search_path)
    elif opt in ("-s", "--secret"):
        secret_path = os.path.realpath(arg)
        print("Will use Google Drive authentication details in " + secret_path)

# Sanity Checks
if (log_path != None) and not os.access(os.path.dirname(log_path), os.W_OK):
    print("ERROR: Unable to write to log. Check permissions.")
    sys.exit(2);
if (search_path == None):
    print("ERROR: Must specify search directory path.")
    print_help();
    sys.exit(2);
if not os.path.isdir(search_path) or not os.access(search_path, os.R_OK):
    print("ERROR: " + search_path + " does not exist, is not a directory, or is not readable.")
    print_help();
    sys.exit(2);
if (secret_path == None):
    print("No search directory specified. Using "+search_path+"/drive.secret.")
    secret_path = search_path+"/drive.secret"
if not os.path.isfile(secret_path) or not os.access(secret_path, os.R_OK):
    print(secret_path + " does not exist, is not a file, or is not readable.")
    print_help();
    sys.exit(2);


log("Welcome to BURPG Echo.")

# csv_files = locate_csv_files()
# video_files = locate_video_files()
