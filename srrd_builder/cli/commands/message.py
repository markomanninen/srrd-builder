#!/usr/bin/env python3
"""
Message CLI Commands
Handle message viewing and management from the command line.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def get_mongo_storage():
    """Get MongoDB storage instance"""
    try:
        # Add the MCP code directory to path
        mcp_dir = Path(__file__).parents[3] / "work" / "code" / "mcp"
        sys.path.insert(0, str(mcp_dir))
        
        from storage.mongo_storage import MongoStorage
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Initialize MongoDB storage
        storage = MongoStorage()
        return storage
    except Exception as e:
        print(f"Error initializing MongoDB storage: {e}")
        print("Make sure MongoDB is running and environment variables are set.")
        return None

def format_message_content(message):
    """Format message content for display"""
    if not message:
        return "Message not found."
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"MESSAGE ID: {message['message_id']}")
    lines.append(f"FROM: {message['sender']}")
    lines.append(f"TO: {message['recipient']}")
    lines.append(f"SENT: {message['timestamp']}")
    lines.append(f"STATUS: {'READ' if message['read_status'] else 'UNREAD'}")
    if message.get('read_at'):
        lines.append(f"READ AT: {message['read_at']}")
    lines.append(f"SIZE: {message.get('size_bytes', 0)} bytes")
    lines.append("=" * 60)
    lines.append("")
    lines.append("MESSAGE:")
    lines.append(message['message'])
    lines.append("")
    
    # Show attachments
    attachments = message.get('attachments', [])
    if attachments:
        lines.append(f"ATTACHMENTS ({len(attachments)}):")
        lines.append("-" * 40)
        for i, att in enumerate(attachments, 1):
            lines.append(f"{i}. {att['filename']} ({att['size']} bytes, {att.get('mime_type', 'unknown')})")
            lines.append("")
            lines.append("Content:")
            lines.append(att['content'])
            lines.append("-" * 40)
    
    return "\n".join(lines)

def format_message_list(messages, username, show_unread_count=True):
    """Format message list for display"""
    if not messages:
        return "No messages found."
    
    lines = []
    
    if show_unread_count:
        unread_count = sum(1 for msg in messages if not msg['read_status'])
        lines.append(f"Messages for {username} ({unread_count} unread, {len(messages)} total)")
        lines.append("=" * 60)
    
    for msg in messages:
        status_icon = "📬 UNREAD" if not msg['read_status'] else "📭 read"
        attachments = f" (📎 {len(msg.get('attachments', []))} files)" if msg.get('attachments') else ""
        
        # Truncate message for list view
        message_preview = msg['message'][:80]
        if len(msg['message']) > 80:
            message_preview += "..."
        
        lines.append(f"{status_icon} {msg['message_id']} from {msg['sender']}")
        lines.append(f"   {msg['timestamp']}{attachments}")
        lines.append(f"   {message_preview}")
        lines.append("")
    
    return "\n".join(lines)

def handle_message_view(args):
    """Handle message view command"""
    storage = get_mongo_storage()
    if not storage:
        return 1
    
    try:
        message = storage.get_message_by_id(args.message_id)
        if not message:
            print(f"Message {args.message_id} not found.")
            return 1
        
        # Mark message as read if the viewer is the recipient and it's unread
        viewer = getattr(args, 'user', None)
        if viewer and viewer == message['recipient'] and not message['read_status']:
            try:
                storage.mark_message_read(args.message_id, viewer)
                message['read_status'] = True  # Update display
                message['read_at'] = datetime.utcnow()
                print(f"✅ Message marked as read for {viewer}")
            except Exception as e:
                print(f"Warning: Could not mark message as read: {e}")
        elif viewer and viewer != message['recipient']:
            print(f"ℹ️  Note: Message is for {message['recipient']}, not {viewer}. Not marked as read.")
        elif not viewer:
            print(f"ℹ️  Tip: Use --user {message['recipient']} to mark this message as read")
        
        print(format_message_content(message))
        return 0
    except Exception as e:
        print(f"Error viewing message: {e}")
        return 1
    finally:
        storage.close()

def handle_message_list(args):
    """Handle message list command"""
    storage = get_mongo_storage()
    if not storage:
        return 1
    
    try:
        messages = storage.get_messages(
            recipient=args.username,
            unread_only=args.unread,
            sender=args.sender
        )
        
        # Limit results
        if len(messages) > args.limit:
            messages = messages[:args.limit]
            print(f"Showing first {args.limit} messages (of {len(messages)} total)")
        
        print(format_message_list(messages, args.username))
        return 0
    except Exception as e:
        print(f"Error listing messages: {e}")
        return 1
    finally:
        storage.close()

def handle_message_conversation(args):
    """Handle message conversation command"""
    storage = get_mongo_storage()
    if not storage:
        return 1
    
    try:
        # Get messages between the two users (both directions)
        messages1 = storage.get_messages(recipient=args.user1, sender=args.user2)
        messages2 = storage.get_messages(recipient=args.user2, sender=args.user1)
        
        # Combine and sort by timestamp
        all_messages = messages1 + messages2
        all_messages.sort(key=lambda x: x['timestamp'])
        
        if not all_messages:
            print(f"No conversation found between {args.user1} and {args.user2}")
            return 0
        
        print(f"Conversation between {args.user1} and {args.user2}")
        print("=" * 60)
        
        for msg in all_messages:
            direction = f"{msg['sender']} → {msg['recipient']}"
            status = " (UNREAD)" if not msg['read_status'] else ""
            attachments = f" (📎 {len(msg.get('attachments', []))} files)" if msg.get('attachments') else ""
            
            print(f"{msg['timestamp']} | {direction}{status}{attachments}")
            print(f"{msg['message_id']}: {msg['message']}")
            print("-" * 40)
        
        return 0
    except Exception as e:
        print(f"Error getting conversation: {e}")
        return 1
    finally:
        storage.close()

def handle_message_stats(args):
    """Handle message stats command"""
    storage = get_mongo_storage()
    if not storage:
        return 1
    
    try:
        # Get all messages for user (sent and received)
        received_messages = storage.get_messages(recipient=args.username)
        
        # Get sent messages by querying with sender field
        # Note: This requires a different query method
        sent_messages = list(storage.db.messages.find({'sender': args.username}))
        
        unread_count = storage.get_unread_count(args.username)
        
        # Get subscriptions
        subscriptions = storage.get_subscriptions(args.username)
        
        print(f"Message Statistics for {args.username}")
        print("=" * 40)
        print(f"Messages received: {len(received_messages)}")
        print(f"Messages sent: {len(sent_messages)}")
        print(f"Unread messages: {unread_count}")
        print(f"Subscriptions: {len(subscriptions)}")
        
        if received_messages:
            latest_received = max(received_messages, key=lambda x: x['timestamp'])
            print(f"Latest received: {latest_received['timestamp']} from {latest_received['sender']}")
        
        if sent_messages:
            latest_sent = max(sent_messages, key=lambda x: x['timestamp'])
            print(f"Latest sent: {latest_sent['timestamp']} to {latest_sent['recipient']}")
        
        return 0
    except Exception as e:
        print(f"Error getting message stats: {e}")
        return 1
    finally:
        storage.close()

def handle_message(args):
    """Main message command handler"""
    if not args.message_subcommand:
        print("Error: No message subcommand specified.")
        print("Use: srrd message {view|list|conversation|stats} --help")
        return 1
    
    if args.message_subcommand == "view":
        return handle_message_view(args)
    elif args.message_subcommand == "list":
        return handle_message_list(args)
    elif args.message_subcommand == "conversation":
        return handle_message_conversation(args)
    elif args.message_subcommand == "stats":
        return handle_message_stats(args)
    else:
        print(f"Unknown message subcommand: {args.message_subcommand}")
        return 1