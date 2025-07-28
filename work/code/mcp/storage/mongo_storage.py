import os
import uuid
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError

class MongoStorage:
    def __init__(self, db_name='mcp_messages'):
        self.client = None
        self.db = None
        self.max_message_size = int(os.environ.get('MAX_MESSAGE_SIZE', 10485760))
        self.max_attachment_size = int(os.environ.get('MAX_ATTACHMENT_SIZE', 52428800))
        self.daily_message_limit = int(os.environ.get('DAILY_MESSAGE_LIMIT', 100))
        self.rate_limit_window = int(os.environ.get('RATE_LIMIT_WINDOW', 60))
        self.max_subscriptions = int(os.environ.get('MAX_SUBSCRIPTIONS', 100))
        
        try:
            mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            self._setup_indexes()
        except ConnectionFailure as e:
            raise Exception(f"Could not connect to MongoDB: {e}") from e

    def _setup_indexes(self):
        """Create database indexes for performance"""
        if self.db is None:
            return
            
        # Index for message queries
        self.db.messages.create_index([("recipient", ASCENDING), ("timestamp", -1)])
        self.db.messages.create_index([("message_id", ASCENDING)], unique=True)
        
        # Index for user queries
        self.db.users.create_index([("username", ASCENDING)], unique=True)
        
        # Index for subscription queries
        self.db.subscriptions.create_index([("subscriber", ASCENDING), ("target", ASCENDING)], unique=True)
        self.db.subscriptions.create_index([("target", ASCENDING)])
    
    def register_user(self, username):
        """Register a new user or update existing user's last_active"""
        if self.db is None:
            raise Exception("Database not initialized.")
            
        now = datetime.utcnow()
        user_doc = {
            "username": username,
            "registered_at": now,
            "last_active": now,
            "rate_limit": {
                "messages_sent_today": 0,
                "last_message_time": None,
                "subscription_count": 0
            }
        }
        
        try:
            self.db.users.insert_one(user_doc)
            return f"User {username} registered successfully"
        except DuplicateKeyError:
            # User exists, update last_active
            self.db.users.update_one(
                {"username": username},
                {"$set": {"last_active": now}}
            )
            return f"User {username} updated last_active"
    
    def get_all_users(self):
        """Get list of all registered users"""
        if self.db is None:
            raise Exception("Database not initialized.")
            
        users = list(self.db.users.find({}, {"username": 1, "last_active": 1, "_id": 0}))
        return users
    
    def subscribe_user(self, subscriber, target):
        """Subscribe user to another user with limits check"""
        if self.db is None:
            raise Exception("Database not initialized.")
            
        # Check if target user exists
        target_user = self.db.users.find_one({"username": target})
        if not target_user:
            raise Exception(f"Target user {target} not found")
            
        # Check subscription limit
        current_subs = self.db.subscriptions.count_documents({"subscriber": subscriber})
        if current_subs >= self.max_subscriptions:
            raise Exception(f"Subscription limit reached ({self.max_subscriptions})")
            
        subscription_doc = {
            "subscriber": subscriber,
            "target": target,
            "subscribed_at": datetime.utcnow()
        }
        
        try:
            self.db.subscriptions.insert_one(subscription_doc)
            # Update subscription count
            self.db.users.update_one(
                {"username": subscriber},
                {"$inc": {"rate_limit.subscription_count": 1}}
            )
            return f"Successfully subscribed to {target}"
        except DuplicateKeyError:
            raise Exception(f"Already subscribed to {target}")
    
    def unsubscribe_user(self, subscriber, target):
        """Unsubscribe user from another user"""
        if self.db is None:
            raise Exception("Database not initialized.")
            
        result = self.db.subscriptions.delete_one({"subscriber": subscriber, "target": target})
        if result.deleted_count > 0:
            # Update subscription count
            self.db.users.update_one(
                {"username": subscriber},
                {"$inc": {"rate_limit.subscription_count": -1}}
            )
            return f"Successfully unsubscribed from {target}"
        else:
            raise Exception(f"Not subscribed to {target}")
    
    def get_subscriptions(self, username):
        """Get list of users that username is subscribed to"""
        if self.db is None:
            raise Exception("Database not initialized.")
            
        subscriptions = list(self.db.subscriptions.find(
            {"subscriber": username},
            {"target": 1, "subscribed_at": 1, "_id": 0}
        ))
        return subscriptions
    
    def _check_rate_limit(self, username):
        """Check if user has exceeded rate limits"""
        if self.db is None:
            raise Exception("Database not initialized.")
            
        user = self.db.users.find_one({"username": username})
        if not user:
            raise Exception(f"User {username} not found")
            
        now = datetime.utcnow()
        rate_limit = user.get('rate_limit', {})
        
        # Check daily limit
        last_message = rate_limit.get('last_message_time')
        messages_today = rate_limit.get('messages_sent_today', 0)
        
        if last_message and (now - last_message).days == 0:
            if messages_today >= self.daily_message_limit:
                raise Exception(f"Daily message limit reached ({self.daily_message_limit})")
                
            # Check rate limit window (messages per minute)
            if (now - last_message).total_seconds() < self.rate_limit_window:
                recent_messages = self.db.messages.count_documents({
                    "sender": username,
                    "timestamp": {"$gte": now - timedelta(seconds=self.rate_limit_window)}
                })
                if recent_messages >= 10:  # 10 messages per minute
                    raise Exception(f"Rate limit exceeded (10 messages per {self.rate_limit_window}s)")
    
    def save_message(self, sender, recipient, message, attachments=None):
        """Save message with rate limiting and file attachments"""
        if self.db is None:
            raise Exception("Database not initialized.")
            
        # Check rate limits
        self._check_rate_limit(sender)
        
        # Check if sender is subscribed to recipient
        subscription = self.db.subscriptions.find_one({"subscriber": sender, "target": recipient})
        if not subscription:
            raise Exception(f"Not subscribed to {recipient}. Use subscribe_to_user first.")
            
        # Check message size
        message_size = len(message.encode('utf-8'))
        if message_size > self.max_message_size:
            raise Exception(f"Message too large ({message_size} bytes, max {self.max_message_size})")
            
        # Process attachments
        processed_attachments = []
        if attachments:
            for attachment in attachments:
                att_size = len(attachment['content'].encode('utf-8'))
                if att_size > self.max_attachment_size:
                    raise Exception(f"Attachment {attachment['filename']} too large ({att_size} bytes, max {self.max_attachment_size})")
                processed_attachments.append(attachment)
        
        # Generate unique message ID
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        
        message_doc = {
            'message_id': message_id,
            'sender': sender,
            'recipient': recipient,
            'message': message,
            'timestamp': now,
            'read_status': False,
            'read_at': None,
            'size_bytes': message_size + sum(len(att['content'].encode('utf-8')) for att in processed_attachments),
            'attachments': processed_attachments
        }

        self.db.messages.insert_one(message_doc)
        
        # Update user rate limit
        user = self.db.users.find_one({"username": sender})
        messages_today = user['rate_limit']['messages_sent_today']
        last_message_time = user['rate_limit'].get('last_message_time')
        
        # Reset daily count if it's a new day
        if not last_message_time or (now - last_message_time).days > 0:
            messages_today = 0
            
        self.db.users.update_one(
            {"username": sender},
            {"$set": {
                "rate_limit.messages_sent_today": messages_today + 1,
                "rate_limit.last_message_time": now
            }}
        )
        
        return message_id

    def get_messages(self, recipient, unread_only=False, sender=None):
        """Get messages for recipient with filtering options"""
        if self.db is None:
            raise Exception("Database not initialized.")
            
        query = {'recipient': recipient}
        if unread_only:
            query['read_status'] = False
        if sender:
            query['sender'] = sender
            
        messages = list(self.db.messages.find(query).sort('timestamp', -1))
        return messages
    
    def get_message_by_id(self, message_id):
        """Get specific message by ID"""
        if self.db is None:
            raise Exception("Database not initialized.")
            
        return self.db.messages.find_one({'message_id': message_id})
    
    def mark_message_read(self, message_id, recipient):
        """Mark message as read"""
        if self.db is None:
            raise Exception("Database not initialized.")
            
        result = self.db.messages.update_one(
            {'message_id': message_id, 'recipient': recipient},
            {'$set': {'read_status': True, 'read_at': datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            return f"Message {message_id} marked as read"
        else:
            raise Exception(f"Message {message_id} not found or not for {recipient}")
    
    def get_unread_count(self, username):
        """Get count of unread messages for user"""
        if self.db is None:
            raise Exception("Database not initialized.")
            
        return self.db.messages.count_documents({'recipient': username, 'read_status': False})

    def delete_message(self, message_id, username):
        """Delete message (only sender or recipient can delete)"""
        if self.db is None:
            raise Exception("Database not initialized.")
            
        result = self.db.messages.delete_one({
            'message_id': message_id,
            '$or': [{'sender': username}, {'recipient': username}]
        })
        
        if result.deleted_count > 0:
            return f"Message {message_id} deleted"
        else:
            raise Exception(f"Message {message_id} not found or no permission to delete")
    
    def close(self):
        if self.client:
            self.client.close()
