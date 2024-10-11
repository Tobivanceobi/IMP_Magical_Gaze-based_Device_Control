import pymongo
import uuid

class MongoDBController:
    def __init__(self, uri="mongodb://130.82.171.231:27017", db_name="gaze_data_db"):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[db_name]

    def create_session(self, session_info):
        session_id = str(uuid.uuid4())  # Generate a unique session ID
        session_info['_id'] = session_id  # Use session_id as the primary key
        self.db.sessions.insert_one(session_info)  # Store session info (name, age, task, etc.)
        print(f"Session {session_id} created.")
        return session_id

    def save_gaze_point(self, session_id, gaze_point):
        try:
            # Insert gaze point into the 'gaze_points' collection within the session
            gaze_point['session_id'] = session_id
            self.db.gaze_points.insert_one(gaze_point)
        except Exception as e:
            print(f"An error occurred while saving the gaze point: {e}")