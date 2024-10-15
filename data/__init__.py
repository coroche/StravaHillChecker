from firebase_admin import credentials, firestore, initialize_app
from google.cloud.firestore_v1.client import Client

cred = credentials.Certificate('data/firebaseServiceAccountKey.json')
initialize_app(cred)
db: Client = firestore.client()