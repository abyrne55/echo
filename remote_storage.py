# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103,E1101
"""
BURPG Echo
See LICENSE for MIT/X11 license info.
See README.md for all other help.

Note: This class was adapted from Google's Drive API Python Quickstart
https://developers.google.com/drive/v3/web/quickstart/python
"""

#from __future__ import print_function
import os
import httplib2

from apiclient import discovery
from apiclient import http
import oauth2client
from oauth2client import client
from oauth2client import tools


class GoogleDrive:
    """
    GoogleDrive provides a way to connect to a user's Google Drive and upload
    files to it
    """

    SCOPES = 'https://www.googleapis.com/auth/drive.file'
    CLIENT_SECRET_FILE = 'client_secrets.json'
    CLIENT_CREDENTIAL_FILE = 'drive.credentials'
    APPLICATION_NAME = 'BURPG Echo'
    CREDENTIALS = None
    DRIVE_SERVICE = None
    logger = None

    def __init__(self, logger, secret_path='client_secrets.json',
                 credentials_path='drive.credentials', noauth_local_webserver=False):
        """
        Gets valid GDrive user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
        """
        self.CLIENT_SECRET_FILE = secret_path
        self.CLIENT_CREDENTIAL_FILE = credentials_path
        self.logger = logger

        credstore = oauth2client.file.Storage(self.CLIENT_CREDENTIAL_FILE)
        credentials = credstore.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME

            # Workaround to prevent tools.run_flow from trying to grab our args
            import argparse
            parser = argparse.ArgumentParser(description=__doc__,
                                             formatter_class=argparse.RawDescriptionHelpFormatter,
                                             parents=[tools.argparser])
            dummy_args = []
            if noauth_local_webserver:
                logger.log_verbose("Performing offline auth-flow")
                dummy_args = ["--noauth_local_webserver"]

            credentials = tools.run_flow(flow, credstore, flags=parser.parse_args(dummy_args))
            self.logger.log_verbose('Storing credentials to ' + self.CLIENT_CREDENTIAL_FILE)
        self.CREDENTIALS = credentials
        self.DRIVE_SERVICE = discovery.build(
            'drive', 'v3', http=credentials.authorize(httplib2.Http()))
        self.logger.log_verbose("Google Drive authentication complete")

    def upload_file(self, file_path, parent_folder_id=None):
        """
        Upload a file to Google Drive in a "chunked" manner

        :param file_path: the local path to the file being uploaded
        :param parent_folder_id: the id of the folder where this file should be
        placed
        :returns: the API's response object
        """
        self.logger.log_verbose("Attempting multipart upload of " + file_path +
                                " into folder " + str(parent_folder_id))
        media = http.MediaFileUpload(file_path, resumable=True)
        file_metadata = {'name': os.path.basename(file_path)}
        if parent_folder_id is not None:
            file_metadata['parents'] = [parent_folder_id]

        request = self.DRIVE_SERVICE.files().create(body=file_metadata, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                self.logger.log_verbose("Uploaded {:d}%.".format(int(status.progress() * 100)))
        self.logger.log_verbose("Upload of " + file_path + " complete!")
        return response

    def create_folder(self, folder_name):
        """
        Creates a folder in Google Drive and returns the ID

        Note: Google Drive treats folders just like files, except that they have
        the special MIME type "application/vnd.google-apps.folder". To place a
        file in a folder, create the folder using this method and then add the
        ID to the "parents" array property of the "body" argument in
        files().create()

        :param folder_name: the desired name of the created folder
        :returns: the ID of the newly-created folder
        """
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        folder = self.DRIVE_SERVICE.files().create(body=folder_metadata, fields='id').execute()
        self.logger.log_verbose("Created folder '" + folder_name + "' with ID " + folder.get('id'))
        return folder.get('id')
