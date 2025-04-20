# firebase_service.py

import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CREDENTIAL_PATH

cred = credentials.Certificate(FIREBASE_CREDENTIAL_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

def save_alert(chat_id, origin, destination, target_price):
    doc_ref = db.collection("alerts").document(str(chat_id))
    doc_ref.set({
        "origin": origin,
        "destination": destination,
        "target_price": target_price
    })

def get_alert(chat_id):
    doc = db.collection("alerts").document(str(chat_id)).get()
    if doc.exists:
        return doc.to_dict()
    return None
