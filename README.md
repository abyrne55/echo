# BURPG Echo
Python tool for automatically uploading rocketry videos and data to Google Drive (EK128)
*Requires Python 3+*

## Installation
1. Satisfy dependencies
  ```bash
  # On Debian/Ubuntu
  sudo apt-get install build-essential gfortran libatlas-base-dev python-pip python-dev
  
  # On Mac OS X or Windows, I'd recommend downloading the Anaconda Python distribution
  # from https://www.continuum.io/downloads
  
  # Run the following commands regardless of your OS. Note, you may need root/admin privileges
  pip install --upgrade pip
  pip install --upgrade numpy scipy matplotlib google-api-python-client
  ```
2. Download/clone the latest source and extract it to your working directory
3. Register for a Google Developers Key (needed to access the Drive API). This step does NOT grant anyone access to your personal Google Drive. It simply gets you a Google API *client ID* and *secret*, which you'll need to access the Drive API.
  1. Use [this wizard](https://console.developers.google.com/start/api?id=drive) to create or select a project in the Google Developers Console and automatically turn on the API. Click **Continue**, then **Go to credentials**.
  2. On the next page, select *Google Drive API* under **Which API are you using**, then select *Other UI (e.g. Windows, CLI tool)* under **Where will you be calling the API from**. Select *User Data* under **What data will you be accessing**. Click **What credentials do I need** to continue.
  3. Set **Name** to *BURPG Echo*, then click **Create client ID**
  4. Select any email address from the **Email address** selector. (Please note that this email may be shown under "Developer Info" as the end-user is signing in.) Set **Product name shown to users** to *BURPG Echo*. Click **Continue**.
  5. Finally, click **Download**, and save the downloaded file as *client_secrets.json* in your working directory
4. You're done! Now read the usage instructions below

**Warning: Keep your *client_secrets.json* file to yourself.** If it's shared, someone could abuse Google's API while using your client ID and secret, which could cause your Google Developer account to be locked down, or worse.

## Basic Usage
1. Ensure the directory you'd like Echo to scan is fully readable by your user, and ensure Echo can write to its working directory
2. Run `python echo.py -p [SEARCH_PATH]`, replacing *[SEARCH_PATH]* with the path to your search directory
3. If you're running Echo for the first time, this will open a web browser allowing you to login to Drive and grant Echo permission to access it. Follow the prompts and return to your terminal once the authentication flow is complete.
4. After successful authentication, echo will generate relevant graphs and upload all relevant files

## Options
Flag | Long Flag | Description | Default Value
------------ | ------------- | ------------- | -------------
-a | --automatic | Generate all graphs and save them to PNG's, without waiting for user action. This is the default mode. | Enabled
-h | --help | Print a short help message | n/a
-i | --interactive | Opposite of -a. Generate all graphs and display them to the user, allowing them to save graphs as needed through matplotlib's interface. Note: this won't work over ssh unless X forwarding is enabled. | Disabled
-l | --log | Log all application output to echo.log. Best used in conjunction with -v | Disabled
-v | --verbose | Be extra chatty about what we're doing. Good for debugging | Disabled
-p [SEARCH_PATH] | --path | (required) The path to the directory that echo should look for video and data files in | n/a
-s [SECRET_PATH] | --secret | Path to the client_secrets.json file required by the Google Drive API | ./client_secrets.json
-c [CREDS_PATH] | --credentials | Path to a drive.credentials file generated by a previous instance of Echo. If this file is expired or nonexistent, echo will start the Google authentication flow | ./drive.credentials
-n | --noauth_local_webserver | Perform the Google authentication flow in "headless mode." Use this if you're logging in for the first time on a remote server or other machine with no GUI | Disabled

## Legal
See LICENSE for MIT/X11 license info.
