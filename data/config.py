import json
import firebase_admin
from firebase_admin import credentials, firestore
from dataclasses import dataclass, asdict
from typing import List
import os
import uuid
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.base_query import FieldFilter
from utils.decorators import trim
from datetime import datetime, timedelta, timezone


cred = credentials.Certificate('data/firebaseServiceAccountKey.json')
firebase_admin.initialize_app(cred)
db: Client = firestore.client()
config_doc_ref = db.collection('config').document('settings')
credentials_doc_ref = db.collection('config').document('credentials')
token_doc_ref = db.collection('config').document('token')

@trim
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
    dashboard_url: str
    test_parameter: str = ''

@trim
@dataclass
class Recipient:
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
    
@trim
@dataclass
class Notification:
    activity_id: int
    recipient_id: str
    kudos: bool = False
    notificationDate: datetime = datetime(1900, 1, 1, 0, 0)


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
    

def getMailingList() -> List[Recipient]:   
    mailingList = db.collection('mailing_list').where(filter=FieldFilter('email_verified', '==', True)).get()
    return [Recipient(id = doc.id, **doc.to_dict()) for doc in mailingList]


def getNotification(activityID: int, recipientID: str) -> Notification:   
    activityNotifications = db.collection('notifications').where(filter=FieldFilter('activity_id', '==', activityID)).where(filter=FieldFilter('recipient_id', '==', recipientID)).get()
    if activityNotifications:
        return [Notification(**doc.to_dict()) for doc in activityNotifications][0]
    else:
        return None

def getActivityNotifications(activityID: int) -> List[Notification]:   
    activityNotifications = db.collection('notifications').where(filter=FieldFilter('activity_id', '==', activityID)).get()
    return [Notification(**doc.to_dict()) for doc in activityNotifications]


def getUnkudosedNotifications(ignoreTimeDiff: bool = False) -> List[Notification]:
    activityNotifications = db.collection('notifications').where(filter=FieldFilter('kudos', '==', False))
    if not ignoreTimeDiff:
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        activityNotifications = activityNotifications.where(filter=FieldFilter('notificationDate', '>=', seven_days_ago))
    return [Notification(**doc.to_dict()) for doc in activityNotifications.get()]


def writeNotification(activityID: int, recipientID: str):   
    notification = Notification(activity_id=activityID, recipient_id=recipientID, notificationDate=datetime.now(timezone.utc))
    collection_ref = db.collection('notifications')
    collection_ref.document(f"{activityID}_{recipientID}").set(asdict(notification))

def deleteNotification(activityID: int, recipientID: str):
    doc_ref = db.collection('notifications').document(f"{activityID}_{recipientID}")
    doc_ref.delete()

def updateNotification(activityID: int, recipientID: str):  
    doc_ref = db.collection('notifications').document(f"{activityID}_{recipientID}")
    doc_ref.update({'kudos': True})


def getRecipient(id: str) -> Recipient:
    data = db.collection('mailing_list').document(id).get().to_dict()
    if data:
        return Recipient(id = id, **data)
    else:
        return None

def getRecipientByEmail(email: str) -> List[Recipient]:
    data = db.collection('mailing_list').where(filter=FieldFilter('email', '==', email)).get()
    return [Recipient(id = doc.id, **doc.to_dict()) for doc in data]

def createRecipient(email: str, onStrava: bool, firstname: str = '', surname: str = '') -> tuple[bool, str, str]:
    if getRecipientByEmail(email):
        return False, 'Email address already subscribed', None
    elif onStrava and (not firstname or not surname):
        return False, 'Name must be provided if on strava', None
    else:
        if surname:
            surname = f'{surname[0]}.'
        recipient = Recipient(id='', email=email, on_strava=onStrava, strava_firstname=firstname, strava_lastname=surname)
        recipient_dict = asdict(recipient)
        recipient_dict.pop('id')
        collection_ref = db.collection('mailing_list')
        _, doc = collection_ref.add(recipient_dict)
        return True, None, doc.id

def deleteRecipient(id: str) -> bool:
    recipient_doc_ref = db.collection('mailing_list').document(id)

    if not recipient_doc_ref.get().exists:
        return False
    
    notification_collection_ref = db.collection('notifications')
    notification_doc_refs = notification_collection_ref.where(filter=FieldFilter('recipient_id', '==', id)).stream()
    for notification in notification_doc_refs:
        notification = notification_collection_ref.document(notification.id)
        notification.delete()
    recipient_doc_ref.delete()
    return True

def verifyRecipientEmail(id: str) -> None:
    doc_ref = db.collection('mailing_list').document(id)
    doc_ref.update({'email_verified': True})


def getHTMLTemplate(filename: str) -> str:
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


def renameField(collection_name: str, old_key_name: str, new_key_name: str) -> None:
    docs = db.collection(collection_name).stream()

    for doc in docs:
        doc_dict = doc.to_dict()
        
        if old_key_name in doc_dict:
            doc.reference.update({
                new_key_name: doc_dict[old_key_name],
                old_key_name: firestore.DELETE_FIELD
            })

