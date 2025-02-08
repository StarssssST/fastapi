from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, db, initialize_app
from pydantic import BaseModel
from typing import Optional
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase Configuration
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyAsdOSHknvHMgUT38nZB6U0hRDayTNbhYk",
    "authDomain": "snote-proj.firebaseapp.com",
    "projectId": "snote-proj",
    "storageBucket": "snote-proj.firebasestorage.app",
    "messagingSenderId": "579062555200",
    "appId": "1:579062555200:web:4facc84d3ded71e45075a5",
    "measurementId": "G-LKEH6FW0ED",
    "databaseURL": "https://snote-proj-default-rtdb.asia-southeast1.firebasedatabase.app/"
}

# Initialize Firebase Admin with the configuration
cred = credentials.Certificate("snote-proj-firebase-adminsdk-fbsvc-571a0352cd.json")
initialize_app(cred, FIREBASE_CONFIG)

class Note(BaseModel):
    title: str
    content: str
    timestamp: Optional[int] = None

@app.post("/notes")
async def create_note(note: Note):
    try:
        ref = db.reference('notes')
        note_data = note.dict()
        new_note_ref = ref.push(note_data)
        return {"id": new_note_ref.key, **note_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notes")
async def get_notes():
    try:
        ref = db.reference('notes')
        notes = ref.get()
        return notes if notes else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    try:
        ref = db.reference(f'notes/{note_id}')
        ref.delete()
        return {"message": "Note deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"root": "this is root btw ;V"}

# New endpoint to get Firebase configuration
@app.get("/firebase-config")
async def get_firebase_config():
    return FIREBASE_CONFIG