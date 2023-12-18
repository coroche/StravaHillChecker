import json
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dataclasses import dataclass, asdict
from typing import List


cred = credentials.Certificate('data/firebaseServiceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
config_doc_ref = db.collection('config').document('settings')
credentials_doc_ref = db.collection('config').document('credentials')
token_doc_ref = db.collection('config').document('token')


class Config:
    def __init__(self, data: dict):
        self.base_url = data.get("base_url")
        self.client_id = data.get("client_id")
        self.client_secret = data.get("client_secret")
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token")
        self.webhook_callback_url = data.get("webhook_callback_url")
        self.webhook_verify_token = data.get("webhook_verify_token")
        self.google_script_ID = data.get("google_script_ID")
        self.last_parsed_activity = data.get("last_parsed_activity")
        self.google_functions_url = data.get("google_functions_url")
        self.smtp_port = data.get('smtp_port')
        self.smtp_server = data.get('smtp_server')
        self.sender_email = data.get('sender_email') 
        self.smtp_password = data.get('smtp_password')
        self.errorEmail = data.get('error_email')
        self.default_email_image = data.get('default_email_image')

@dataclass
class Receipient:
    email: str
    on_strava: bool
    strava_firstname: str
    strava_lastname: str
    
    @property
    def strava_fullname(self) -> str:
        return self.strava_firstname + self.strava_lastname
    
@dataclass
class Notification:
    activity_id: int
    strava_fullname: str
    kudos: bool = False

def getConfig() -> Config:   
    config_data = config_doc_ref.get().to_dict()  
    config = Config(config_data)
    return config


def get(parameter: str):       
    data = config_doc_ref.get().to_dict()
    return data[parameter]


def write(parameter: str, value):   
    config_doc_ref.update({parameter: value})


def getCredentials() -> dict:
    data = credentials_doc_ref.get().to_dict()
    return data


def getToken() -> dict:
    data = None
    data = token_doc_ref.get().to_dict()
    return data


def writeToken(token_data: str):   
    token_data = json.loads(token_data)
    token_doc_ref.update(token_data)
    

def getMailingList() -> List[Receipient]:   
    mailingList = db.collection('mailing_list').get()
    return [Receipient(**doc.to_dict()) for doc in mailingList]


def getActivityNotifications(activityID: int) -> List[Notification]:   
    activityNotifications = db.collection('notifications').where('activity_id', '==', activityID).get()
    return [Notification(**doc.to_dict()) for doc in activityNotifications]


def writeNotification(activityID, strava_fullname):   
    notification = Notification(activityID, strava_fullname)
    collection_ref = db.collection('notifications')
    collection_ref.document(f"{activityID}_{strava_fullname}").set(asdict(notification))

    

