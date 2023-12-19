import json
import firebase_admin
from firebase_admin import credentials, firestore
from dataclasses import dataclass, asdict
from typing import List


cred = credentials.Certificate('data/firebaseServiceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
config_doc_ref = db.collection('config').document('settings')
credentials_doc_ref = db.collection('config').document('credentials')
token_doc_ref = db.collection('config').document('token')

@dataclass
class Config:
    base_url: str
    client_id: str
    client_secret: str
    access_token: str
    refresh_token: str
    webhook_callback_url: str
    webhook_verify_token: str
    google_script_ID: str
    last_parsed_activity: str
    google_functions_url: str
    smtp_port: str
    smtp_server: str
    sender_email: str 
    smtp_password: str
    error_email: str
    default_email_image: str
    test_parameter: str = ''

@dataclass
class Receipient:
    id: str
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
    receipient_id: str
    kudos: bool = False

def getConfig() -> Config:   
    config_data = config_doc_ref.get().to_dict()  
    config = Config(**config_data)
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
    return [Receipient(id = doc.id, **doc.to_dict()) for doc in mailingList]


def getNotification(activityID: int, receipientID: str) -> Notification:   
    activityNotifications = db.collection('notifications').where('activity_id', '==', activityID).where('receipient_id', '==', receipientID).get()
    if activityNotifications:
        return [Notification(**doc.to_dict()) for doc in activityNotifications][0]
    else:
        return None

def getActivityNotifications(activityID: int) -> List[Notification]:   
    activityNotifications = db.collection('notifications').where('activity_id', '==', activityID).get()
    return [Notification(**doc.to_dict()) for doc in activityNotifications]


def getUnkudosedNotifications() -> List[Notification]:   
    activityNotifications = db.collection('notifications').where('kudos', '==', False).get()
    return [Notification(**doc.to_dict()) for doc in activityNotifications]


def writeNotification(activityID: int, receipientID: str):   
    notification = Notification(activityID, receipientID)
    collection_ref = db.collection('notifications')
    collection_ref.document(f"{activityID}_{receipientID}").set(asdict(notification))

def deleteNotification(activityID: int, receipientID: str):
    doc_ref = db.collection('notifications').document(f"{activityID}_{receipientID}")
    doc_ref.delete()

def updateNotification(activityID: int, receipientID: str):  
    doc_ref = db.collection('notifications').document(f"{activityID}_{receipientID}")
    doc_ref.update({'kudos': True})


def getReceipient(id: str) -> Receipient:
    data = db.collection('mailing_list').document(id).get().to_dict()
    return Receipient(id = id, **data)

    

