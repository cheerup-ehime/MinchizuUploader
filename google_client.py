import os
import gspread as gs

from oauth2client.service_account import ServiceAccountCredentials


def create_google_client(access_json=None):
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    if access_json is None:
        access_json = os.environ.get('GOOGLE_ACCESS_KEY_JSON')
    path = os.path.expanduser(access_json)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
    client = gs.authorize(credentials)
    return client


