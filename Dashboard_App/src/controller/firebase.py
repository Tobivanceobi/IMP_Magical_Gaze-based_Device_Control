import firebase_admin
from firebase_admin import credentials, firestore
import uuid

class FirebaseController:
    def __init__(self, cred_path):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def create_session(self, session_info):
        session_id = str(uuid.uuid4())  # Generate a unique session ID
        doc_ref = self.db.collection('gaze_data').document(session_id)
        doc_ref.set(session_info)  # Store session info (name, age, task, etc.)
        print(f"Session {session_id} created.")
        return session_id

    def save_gaze_point(self, session_id, gaze_point):
        try:
            # Add gaze point to the 'gaze_points' sub-collection within the session
            self.db.collection('gaze_data').document(session_id).collection('gaze_points').add(gaze_point)
        except Exception as e:
            print(f"An error occurred while saving the gaze point: {e}")