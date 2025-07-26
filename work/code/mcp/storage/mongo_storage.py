import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoStorage:
    def __init__(self, db_name='mcp_messages'):
        self.client = None
        self.db = None
        try:
            mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
        except ConnectionFailure as e:
            raise Exception(f"Could not connect to MongoDB: {e}") from e

    def save_message(self, sender, recipient, message):
        if not self.db:
            raise Exception("Database not initialized.")

        message_doc = {
            'sender': sender,
            'recipient': recipient,
            'message': message,
            'timestamp': os.times().user
        }

        self.db.messages.insert_one(message_doc)

    def get_messages(self, recipient):
        if not self.db:
            raise Exception("Database not initialized.")

        return list(self.db.messages.find({'recipient': recipient}))

    def close(self):
        if self.client:
            self.client.close()
