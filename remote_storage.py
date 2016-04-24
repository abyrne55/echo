# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103,E1101,R0903
"""
BURPG Echo
See LICENSE for MIT/X11 license info.
See README.md for all other help.

Note: This class was adapted from Google's Drive API Python Quickstart
https://developers.google.com/drive/v3/web/quickstart/python
"""

from __future__ import print_function
import httplib2

from apiclient import discovery
from apiclient import http
import oauth2client
from oauth2client import client
from oauth2client import tools


class RemoteStorage:
    """
    RemoteStorage provides a way to connect to an external drive (such as an FTP
    share or Google Drive) and upload files to it
    """

    SCOPES = 'https://www.googleapis.com/auth/drive.file'
    CLIENT_SECRET_FILE = 'drive.secret'
    CLIENT_CREDENTIAL_FILE = 'drive.credentials'
    APPLICATION_NAME = 'BURPG Echo'
    CREDENTIALS = None
    DRIVE_SERVICE = None

    def __init__(self, secret_path='drive.secret', credential_path='drive.credentials'):
        """
        Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
        """
        self.CLIENT_SECRET_FILE = secret_path
        self.CLIENT_CREDENTIAL_FILE = credential_path

        credstore = oauth2client.file.Storage(self.CLIENT_CREDENTIAL_FILE)
        credentials = credstore.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME

            import argparse
            parser = argparse.ArgumentParser(description=__doc__,
                                             formatter_class=argparse.RawDescriptionHelpFormatter,
                                             parents=[tools.argparser])

            credentials = tools.run_flow(flow, credstore, flags=parser.parse_args([]))
            print('Storing credentials to ' + self.CLIENT_CREDENTIAL_FILE)
        self.CREDENTIALS = credentials
        self.DRIVE_SERVICE = discovery.build(
            'drive', 'v3', http=credentials.authorize(httplib2.Http()))

    def upload_file(self, file_path):
        """
        Upload a file to Google Drive in a "chunked" manner
        """
        media = http.MediaFileUpload(file_path, resumable=True)
        request = self.DRIVE_SERVICE.files().create(media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print("Uploaded {:d}%.".format(int(status.progress() * 100)))
        print("Upload Complete!")
        return response
