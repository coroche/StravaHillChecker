import json
import firebase_admin
from firebase_admin import credentials, firestore
from dataclasses import dataclass, asdict
from typing import List
import os
import uuid


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
    google_maps_api_key: str
    map_icon_bucket: str
    test_parameter: str = ''

@dataclass
class Receipient:
    id: str
    email: str
    on_strava: bool
    strava_firstname: str = ''
    strava_lastname: str = ''
    email_verified: bool = False
    verification_token: str = str(uuid.uuid4())
    
    @property
    def strava_fullname(self) -> str:
        return self.strava_firstname + self.strava_lastname
    
@dataclass
class Notification:
    activity_id: int
    receipient_id: str
    kudos: bool = False

#Remove unwanted dictionary keys before constructing class instance
def trimData(json_data: dict, dClass: type) -> dict:
    return {key: value for key, value in json_data.items() if key in dClass.__annotations__}

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
    mailingList = db.collection('mailing_list').where('email_verified', '==', True).get()
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
    if data:
        return Receipient(id = id, **data)
    else:
        return None

def getReceipientByEmail(email: str) -> List[Receipient]:
    data = db.collection('mailing_list').where('email', '==', email).get()
    return [Receipient(id = doc.id, **doc.to_dict()) for doc in data]

def createReceipient(email: str, onStrava: bool, firstname: str = '', surname: str = '') -> tuple[bool, str, str]:
    if getReceipientByEmail(email):
        return False, 'Email address already subscribed', None
    elif onStrava and (not firstname or not surname):
        return False, 'Name must be provided if on strava', None
    else:
        if surname:
            surname = f'{surname[0]}.'
        receipient = Receipient('', email, onStrava, firstname, surname)
        receipient_dict = asdict(receipient)
        receipient_dict.pop('id')
        collection_ref = db.collection('mailing_list')
        _, doc = collection_ref.add(receipient_dict)
        return True, None, doc.id

def deleteReceipient(id: str) -> bool:
    receipient_doc_ref = db.collection('mailing_list').document(id)

    if not receipient_doc_ref.get().exists:
        return False
    
    notification_collection_ref = db.collection('notifications')
    notification_doc_refs = notification_collection_ref.where('receipient_id', '==', id).stream()
    for notification in notification_doc_refs:
        notification = notification_collection_ref.document(notification.id)
        notification.delete()
    receipient_doc_ref.delete()
    return True

def verifyReceipientEmail(id: str) -> None:
    doc_ref = db.collection('mailing_list').document(id)
    doc_ref.update({'email_verified': True})


def getHTMLTemplate(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'html_templates', filename)

    with open(file_path, 'r') as file:
        html_content = file.read()
    return html_content

def addFieldToDocs(collection_name: str, new_field_name: str, default_value: any) -> None:
    docs = db.collection(collection_name).stream()

    for doc in docs:
        doc_dict = doc.to_dict()
        if new_field_name not in doc_dict:
            doc.reference.update({
                new_field_name: default_value
            })


def removeFieldFromDocs(collection_name: str, field_to_delete: str) -> None:
    docs = db.collection(collection_name).stream()

    for doc in docs:
        doc_dict = doc.to_dict()
        if field_to_delete in doc_dict:
            doc.reference.update({
                field_to_delete: firestore.DELETE_FIELD
        })
    

