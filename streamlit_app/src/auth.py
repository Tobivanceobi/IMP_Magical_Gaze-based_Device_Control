import os

import requests
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from firebase_admin import firestore


# Load Firebase API key from .local/firebase_config.json
config_path = os.path.join(".local", "firebase_config.json")
with open(config_path) as config_file:
    firebase_config = json.load(config_file)

FIREBASE_WEB_API_KEY = firebase_config["FIREBASE_WEB_API_KEY"]
FIREBASE_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"


class FirebaseAuth:
    def __init__(self, cred_path):
        self.cred_path = cred_path
        self.initialize_firebase()

    def initialize_firebase(self):
        # Initialize Firebase only once
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.cred_path)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()  # Firestore client

    def login(self, email, password):
        # Login using Firebase REST API
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(FIREBASE_SIGNIN_URL, data=json.dumps(payload))
        if response.status_code == 200:
            data = response.json()
            st.session_state['id_token'] = data['idToken']
            st.session_state['user'] = data['localId']  # Firebase user ID
            st.success(f"Logged in as {data['email']}")
            return True
        else:
            st.error("Invalid email or password")
            return False

    def register(self, email, password):
        try:
            # Register a new user via Firebase Admin SDK
            user = firebase_auth.create_user(
                email=email,
                password=password
            )
            st.success(f"Successfully created user: {user.email}")
            return True
        except Exception as e:
            st.error(f"Error creating user: {e}")
            return False

    def logout(self):
        if 'id_token' in st.session_state:
            del st.session_state['id_token']
            del st.session_state['user']
            st.success("Logged out successfully!")
