import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import errors
from googleapiclient.discovery import build, Resource
from typing import List
from datetime import datetime
import config

class Hill:
    def __init__(self, data: dict):
        self.id: int = data.get("#")
        self.name: str = data.get("Summit or Place")
        self.latitude: float = data.get("Latitude")
        self.longitude: float = data.get("Longitude")
        self.done: bool = data.get("DoneBool")

    def asDict(self):
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'done': self.done,
            }


def login() -> Credentials:
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    token_data = config.getToken()
    if token_data is not None:
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_data = config.getCredentials()
            flow = InstalledAppFlow.from_client_config(
                credentials_data, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        config.writeToken(creds.to_json())
    return creds


def buildService(creds) -> Resource:
    try:
        service = build('script', 'v1', credentials=creds)
    except errors.HttpError as error:
        print(error.content)
    return service


def getPeaks(SCRIPT_ID: str, service: Resource) -> List[Hill]:
    request = {"function": 'getPeaks',
                "parameters": "",
                "devMode": True}
    try:
        response = service.scripts().run(body=request, scriptId=SCRIPT_ID).execute()
        hills = []
        for hill_data in json.loads(response['response']['result']):
            hills.append(Hill(hill_data))
        return hills
    except errors.HttpError as error:
        print(error.content)


def markAsDone(SCRIPT_ID: str, service: Resource, peakIDs: List[int], dateClimbed: datetime, activityID: int):
    request = {"function": 'markAsDoneByIDs',
                "parameters": [peakIDs, dateClimbed.strftime('%Y-%m-%d'), activityID],
                "devMode": True}
    try:
        service.scripts().run(body=request, scriptId=SCRIPT_ID).execute()
    except errors.HttpError as error:
        print(error.content)


