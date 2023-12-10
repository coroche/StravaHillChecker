import json
import firebase_admin
from firebase_admin import credentials, firestore
import os

is_running_on_gcp = os.getenv('FUNCTION_TARGET') is not None

#Manage settings with Firestore only if running on GCP
if is_running_on_gcp:
    cred = credentials.Certificate('data/firebaseServiceAccountKey.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    config_doc_ref = db.collection('config').document('settings')
    credentials_doc_ref = db.collection('config').document('credentials')
    token_doc_ref = db.collection('config').document('token')
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_dir, '..', 'data', 'config.json')
    credentials_file_path = os.path.join(current_dir, '..', 'data', 'credentials.json')
    token_file_path = os.path.join(current_dir, '..', 'data', 'token.json')

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
    if is_running_on_gcp:
        config_data = config_doc_ref.get().to_dict()

    else:
        with open(config_file_path) as file:
            config_data = json.load(file)
    
    config = Config(config_data)
    return config


def get(parameter: str):    
    if is_running_on_gcp:
        data = config_doc_ref.get().to_dict()
    
    else:
        with open(config_file_path) as file:
            data = json.load(file)
    
    return data[parameter]


def write(parameter: str, value):   
    if is_running_on_gcp:
        config_doc_ref.update({parameter: value})

    else:
        with open(config_file_path, 'r+') as file:
            data = json.load(file)
            data[parameter] = value
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()


def getCredentials() -> dict:
    if is_running_on_gcp:
        data = credentials_doc_ref.get().to_dict()
    
    elif os.path.exists(credentials_file_path):
        with open(credentials_file_path) as file:
            data = json.load(file)

    return data

def getToken() -> dict:
    data = None

    if is_running_on_gcp:
        data = token_doc_ref.get().to_dict()
    
    elif os.path.exists(token_file_path):
        with open(token_file_path) as file:
            data = json.load(file)

    return data


def writeToken(token_data: str):
    if is_running_on_gcp:
        token_data = json.loads(token_data)
        token_doc_ref.update(token_data)
    
    elif os.path.exists(token_file_path):
        with open(token_file_path, 'w') as token:
            token.write(token_data)

