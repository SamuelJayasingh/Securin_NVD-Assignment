import firebase_admin
from firebase_admin import credentials, firestore

def init_firestore():
    cred = credentials.Certificate("firebase_credentials.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    return firestore.client()
