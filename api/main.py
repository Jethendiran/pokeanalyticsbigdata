from fastapi import FastAPI, HTTPException, Query
from database.firebase_connection import get_firestore_client

app = FastAPI(
    title="PokéAnalytics API",
    description="Big Data API for Pokémon TCG Battle Analysis",
    version="1.0.0"
)

db = get_firestore_client()


@app.get("/")
def home():
    return {
        "project": "PokéAnalytics",
        "message": "Pokémon TCG Analytics API is running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    try:
        db.collection("analytics").document("overall_summary").get()
        return {
            "status": "healthy",
            "firebase": "connected"
        }
    except Exception as error:
        raise HTTPException(status_code=503, detail=str(error))


@app.get("/analytics")
def get_analytics():
    document = db.collection("analytics").document("overall_summary").get()

    if not document.exists:
        raise HTTPException(status_code=404, detail="Analytics not found")

    return document.to_dict()


@app.get("/cards")
def get_cards(
    limit: int = Query(default=50, ge=1, le=200)
):
    documents = db.collection("cards").limit(limit).stream()

    return [
        {"document_id": doc.id, **doc.to_dict()}
        for doc in documents
    ]


@app.get("/cards/{card_id}")
def get_card(card_id: str):
    document = db.collection("cards").document(card_id).get()

    if not document.exists:
        raise HTTPException(status_code=404, detail="Card not found")

    return {"document_id": document.id, **document.to_dict()}


@app.get("/battles")
def get_battles(
    limit: int = Query(default=20, ge=1, le=100)
):
    documents = db.collection("battles").limit(limit).stream()

    return [
        {"document_id": doc.id, **doc.to_dict()}
        for doc in documents
    ]


@app.get("/battles/{episode_id}")
def get_battle(episode_id: str):
    document = db.collection("battles").document(episode_id).get()

    if not document.exists:
        raise HTTPException(status_code=404, detail="Battle not found")

    return {"document_id": document.id, **document.to_dict()}
