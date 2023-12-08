import json
import firebase_admin
from firebase_admin import credentials, firestore
import os

def is_running_on_gcp():
    return os.getenv('FUNCTION_TARGET') is not None

#Manage settings with Firestore only if running on GCP
if is_running_on_gcp():
    cred = credentials.Certificate('firebaseServiceAccountKey.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    doc_ref = db.collection('config').document('settings')

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

def getConfig() -> Config:
    
    if is_running_on_gcp():
        config_data = doc_ref.get().to_dict()

    else:
        with open('config.json') as file:
            config_data = json.load(file)
    
    config = Config(config_data)
    return config


def get(parameter: str):
    
    if is_running_on_gcp():
        data = doc_ref.get().to_dict()
    
    else:
        with open('config.json') as file:
            data = json.load(file)
    
    return data[parameter]


def write(parameter: str, value):
    
    if is_running_on_gcp():
        doc_ref.update({parameter: value})

    else:
        with open('config.json', 'r+') as file:
            data = json.load(file)
            data[parameter] = value
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()