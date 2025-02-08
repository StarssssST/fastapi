from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, db, initialize_app
from pydantic import BaseModel
from typing import Optional, Dict
import json
import os

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
try:
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # Get raw private key and fix formatting
        private_key = os.environ.get("private_key", "")
        # Remove any quotes at the start and end
        private_key = private_key.strip('"').strip("'")
        # Ensure proper line endings
        private_key = private_key.replace("\\n", "\n")
        
        service_account_dict = {
            "type": os.environ.get("type"),
            "project_id": os.environ.get("project_id"),
            "private_key_id": os.environ.get("private_key_id"),
            "private_key": private_key,
            "client_email": os.environ.get("client_email"),
            "client_id": os.environ.get("client_id"),
            "auth_uri": os.environ.get("auth_uri"),
            "token_uri": os.environ.get("token_uri"),
            "auth_provider_x509_cert_url": os.environ.get("auth_provider_x509_cert_url"),
            "client_x509_cert_url": os.environ.get("client_x509_cert_url"),
            "universe_domain": os.environ.get("universe_domain")
        }
        
        # Debug output
        print("Private key first line:", private_key.split('\n')[0])
        print("Private key last line:", private_key.split('\n')[-1])
        
        # Remove None values
        service_account_dict = {k: v for k, v in service_account_dict.items() if v is not None}
        
        cred = credentials.Certificate(service_account_dict)
    else:
        # Local development - use JSON file
        cred = credentials.Certificate("snote-proj-firebase-adminsdk-fbsvc-571a0352cd.json")
    
    initialize_app(cred, FIREBASE_CONFIG)
except Exception as e:
    print(f"Firebase initialization error: {str(e)}")
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        print("Environment variables:")
        for key in ["type", "project_id", "private_key_id", "client_email"]:
            print(f"{key}: {os.environ.get(key, 'NOT SET')}")
    raise

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