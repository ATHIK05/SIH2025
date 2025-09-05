import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase app if not already initialized
if not firebase_admin._apps:
    # Try to get credentials from environment variable first
    service_account_key = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY')
    
    if service_account_key:
        # Parse the JSON string from environment variable
        cred_dict = json.loads(service_account_key)
        cred = credentials.Certificate(cred_dict)
    else:
        # Fallback to file path (for local development)
        SERVICE_ACCOUNT_PATH = os.path.join(os.path.dirname(__file__), 'sih2025-f61be-firebase-adminsdk-fbsvc-7abb48115a.json')
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'sih2025-f61be.appspot.com'
    })

def get_firestore_client():
    return firestore.client()

def get_storage_bucket():
    return storage.bucket()
