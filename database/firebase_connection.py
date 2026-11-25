import firebase_admin
from firebase_admin import credentials, firestore

PROJECT_ID = "pokeanalytics-bigdata"

def get_firestore_client():
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()

        firebase_admin.initialize_app(
            cred,
            {"projectId": PROJECT_ID}
        )

    return firestore.client()

if __name__ == "__main__":
    db = get_firestore_client()

    print("Firebase Admin initialized successfully!")

    collections = db.collections()

    print("Firestore connection verified.")

    for collection in collections:
        print("Collection found:", collection.id)
