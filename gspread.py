import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'My Kakeibo'
SPREADSHEET_ID = ''

class Gspread:
    # If modifying these scopes, delete your previously saved credentials
    # at ~/.credentials/sheets.googleapis.com-python-quickstart.json

    def __init__(self, flags):
        self.flags = flags
        self.spreadsheet_id = SPREADSHEET_ID
        self.credential_name = flags.credential
        print("Authentication Start")
        self.service = self.__auth()
        print("Authentication End")

    def __get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        #home_dir = os.path.expanduser('~')
        #credential_dir = os.path.join(home_dir, '.credentials')
        credential_dir = os.path.join(os.path.abspath(os.path.curdir), '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, self.credential_name)

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if self.flags:
                credentials = tools.run_flow(flow, store, self.flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def __auth(self):
        credentials = self.__get_credentials()
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discoveryUrl)
        return service

    def create_new_sheet(self, sheet_name):
        """ exclude index field because new sheet is wanted to
        add the last of the existing sheets
        """
        print("create sheet:", sheet_name, "start")
        req = []
        req.append({
            "addSheet" : {
                "properties" : {
                    "title" : sheet_name,
                }
            }
        })
        body = {"requests" : req}
        resp = self.service.spreadsheets() \
                           .batchUpdate(spreadsheetId=self.spreadsheet_id, body=body) \
                           .execute()
        print("create sheet:", sheet_name, "end")
        req = []
        return resp

    def append_data(self, range_name, value_input_option, values):
        print("append data start")
        body = {"values" : values}
        result = self.service.spreadsheets().values() \
                                            .append(spreadsheetId=self.spreadsheet_id,
                                                    body=body,
                                                    valueInputOption=value_input_option,
                                                    range=range_name) \
                                            .execute()
        print("append data end")
        return result

