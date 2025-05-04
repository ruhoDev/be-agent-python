from flask import Flask, request, jsonify
from slack_service import SlackService
from firebase_service import FirebaseService
from agency import generate_response
import re
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Initialize services
firebase_service = FirebaseService()
slack_service = SlackService()

# Initialize Flask app
flask_app = Flask(__name__)

# Keep track of processed events to prevent duplicate processing
# Format: {event_id: timestamp}
processed_events = {}
EVENT_EXPIRY_TIME = 60  # Seconds to keep events in memory

def clean_old_events():
    """Remove old events from the processed_events dict"""
    current_time = time.time()
    to_remove = []
    for event_id, timestamp in processed_events.items():
        if current_time - timestamp > EVENT_EXPIRY_TIME:
            to_remove.append(event_id)
    
    for event_id in to_remove:
        processed_events.pop(event_id, None)

def process_message(text, conversation_id=None, agent_config=None):
    """Process a message through the agency"""
    try:
        # Use the generate_response function from agency.py
        result = generate_response(text, conversation_id, agent_config)
        return result
    except Exception as e:
        print('error', e)
        raise e

def setup_bot_handlers(slack_app, agent_config):
    """Set up event handlers for a Slack bot"""
    print(f"Setting up handlers for bot with agent config: {agent_config['name'] if agent_config else 'None'}")
    
    # Use separate handlers for app_mention and message to better control the flow
    @slack_app.event("app_mention")
    def handle_app_mention(event, say):
        # Generate unique event ID
        event_id = f"{event.get('client_msg_id', '')}:{event.get('ts', '')}"
        
        # Skip if we've already processed this event
        if event_id in processed_events:
            print(f"Skipping already processed app_mention event: {event_id}")
            return
        
        # Mark as processed
        processed_events[event_id] = time.time()
        clean_old_events()
        
        # Skip messages from bots
        if event.get("bot_id"):
            return
            
        # Skip messages in threads
        if event.get("thread_ts"):
            return
            
        # Process the app mention
        _process_event(event, say, agent_config, slack_app, is_app_mention=True)
    
    @slack_app.event("message")
    def handle_message(event, say):
        # Only process messages, not message subtypes like message_changed, message_deleted, etc.
        if event.get("subtype") is not None:
            return

        # Skip messages from bots
        if event.get("bot_id"):
            return
            
        # Skip messages in threads
        if event.get("thread_ts"):
            return
         
        # Generate unique event ID
        event_id = f"{event.get('client_msg_id', '')}:{event.get('ts', '')}"
        
        # Skip if we've already processed this event
        if event_id in processed_events:
            print(f"Skipping already processed message event: {event_id}")
            return
        
        # Mark as processed
        processed_events[event_id] = time.time()
        clean_old_events()
                
        # Skip messages that mention the bot (these are handled by app_mention)
        text = event.get("text", "")
        if "<@" in text:
            # Check if this message mentions our bot
            auth_test = slack_app.client.auth_test()
            bot_user_id = auth_test.get("user_id")
            
            if f"<@{bot_user_id}>" in text:
                print(f"Skipping message with bot mention (will be handled by app_mention): {event_id}")
                return
        
        # Process regular message
        _process_event(event, say, agent_config, slack_app, is_app_mention=False)

def _process_event(event, say, agent_config, slack_app, is_app_mention=False):
    """Internal function to process an event after filtering""" 
    # Get user information
    try:
        user_id = event["user"]
        user_info = slack_app.client.users_info(user=user_id)
        message_text = event.get("text", "")
                # Get user's real name
        real_name = user_info["user"]["profile"]["real_name"]
        
        # Create full message with user name
        message = real_name + ": " + message_text
        
        # Create conversation ID from channel and thread/message ID
        conversation_id = f"{event['channel']}:{event.get('thread_ts', event['ts'])}"
                
        # Generate response from the agency with conversation persistence
        response = process_message(message, conversation_id, agent_config)
        say(
            text=response,
        )
        
    except Exception as e:
        print(e)
        # say(
        #     text=f"❌ Error: {str(e)}",
        # )

# API endpoint for direct chat requests
@flask_app.route("/chat", methods=["POST"])
def chat_api():
    """Handle direct chat requests via API"""
    try:
        # Get request data
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract required fields
        agent_id = data.get("agent_id")
        message = data.get("message")
        user_id = request.headers.get("X-User-ID")
        # Create conversation_id from agent_id, user_id, and "demo_chat"
        conversation_id = f"{agent_id}:{user_id}:demo_chat" if not data.get("conversation_id") else data.get("conversation_id")
        
        # Validate required fields
        if not agent_id:
            return jsonify({"error": "agent_id is required"}), 400
        if not message:
            return jsonify({"error": "message is required"}), 400
        
        # Log the request
        print(f"Chat request - agent_id: {agent_id}, user_id: {user_id}, conversation_id: {conversation_id}")
        
        # Get agent configuration
        agent_config = firebase_service.get_agent(agent_id)
        if not agent_config:
            return jsonify({"error": f"Agent not found with ID: {agent_id}"}), 404
        
        # Process the message
        response_text = process_message(message, conversation_id, agent_config)
        
        # Return the response
        return jsonify({
            "response": response_text,
            "agent_id": agent_id,
            "conversation_id": conversation_id
        })
        
    except Exception as e:
        print(f"Error in chat API: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Dynamic Slack bot endpoints
@flask_app.route("/slack/events/<bot_id>", methods=["POST"])
def slack_events(bot_id):
    """Handle Slack events for a specific bot"""
    print(f"Received request for bot ID: {bot_id}")
    
    # Handle Slack URL verification challenge
    if request.json and "challenge" in request.json:
        return request.json["challenge"]
    
    # Get the Slack app for this bot
    slack_app, handler = slack_service.get_bot_app(bot_id)
    
    if not slack_app:
        print(f"No slack app found for bot ID: {bot_id}")
        return "Bot not found", 404
    
    # Get agent configuration for this bot
    agent_config = slack_service.get_agent_for_bot(bot_id)
    if not agent_config:
        print(f"No agent configuration found for bot ID: {bot_id}")
    
    # Set up event handlers if not already set
    if not hasattr(slack_app, "_handlers_set"):
        setup_bot_handlers(slack_app, agent_config)
        slack_app._handlers_set = True
    
    # Handle the request
    return handler.handle(request)

# Flask root endpoint
@flask_app.route("/")
def index():
    return "Chat Agency Bot Server is running!"

# Run Flask app
if __name__ == "__main__":
    # Preload active bots
    active_bots = slack_service.get_all_active_bots()
    print(f"Preloaded {len(active_bots)} active Slack bots")
    
    # Run Flask app
    flask_app.run(debug=True, port=5000) 