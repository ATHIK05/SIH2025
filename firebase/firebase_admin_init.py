import firebase_admin
from firebase_admin import credentials, firestore, storage
import os

# Path to your service account key
SERVICE_ACCOUNT_PATH = os.path.join(os.path.dirname(__file__), 'sih2025-f61be-firebase-adminsdk-fbsvc-7abb48115a.json')

# Initialize Firebase app if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'sih2025-f61be.appspot.com'
    })

def get_firestore_client():
    return firestore.client()

def get_storage_bucket():
    return storage.bucket()
