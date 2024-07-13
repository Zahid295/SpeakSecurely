from datetime import datetime, timezone
messages = []

def store_message(sender_id, recipient_id, body):
    messages.append({
        'sender_id': sender_id,
        'recipient_id': recipient_id,
        'body': body,
        'timestamp': datetime.now(timezone.utc)
    })

def get_messages_for_user(user_id):
    user_messages = [msg for msg in messages if msg['recipient_id'] == user_id]
    return user_messages
