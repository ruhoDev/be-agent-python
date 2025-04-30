from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler
from flask import Flask, request
from dotenv import load_dotenv
import os
import asyncio
import re
import concurrent.futures
from functools import partial
from agency import agency
import threading
load_dotenv()

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")  # Required for Socket Mode

# Initialize the Slack app
bolt_app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
flask_app = Flask(__name__)
handler = SlackRequestHandler(bolt_app)

# Thread pool for running synchronous agency methods
executor = concurrent.futures.ThreadPoolExecutor()
# Event loop for async operations
loop = None

async def process_message_async(text):
    """Process a message through the agency asynchronously"""
    try:
        # Run agency with timeout protection
        result = await asyncio.wait_for(async_get_completion(text), timeout=60)
        return result
    except asyncio.TimeoutError:
        return "⏱️ The response timed out. Please try a shorter or simpler query."
    except Exception as e:
        return f"❌ Error: {str(e)}"

async def async_get_completion(text):
    """Wrapper to make synchronous get_completion work asynchronously"""
    loop = asyncio.get_running_loop()
    # Run the synchronous method in a thread pool
    return await loop.run_in_executor(
        executor,  # Use our thread pool
        lambda: agency.get_completion(text, yield_messages=False)
    )

async def process_slack_message_async(text, say):
    """Handle Slack messages by processing them through the agency asynchronously"""
    print(f"[Slack] Processing: {text}")
    
    try:
        # Process the message asynchronously
        result = await process_message_async(text)
        print(f"[Slack] Result: {result}")
        say(result)
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(f"[Slack] Error: {str(e)}")
        # say(error_msg)

def clean_user_text(user_text):
    # Find all user mentions in the format <@U12345678>
    user_mentions = re.findall(r'<@([A-Z0-9]+)>', user_text)
    
    # Replace each user mention with a cleaner format
    clean_text = user_text
    for user_id in user_mentions:
        try:
            # Get user info from Slack API
            user_info = bolt_app.client.users_info(user=user_id)
            user_name = user_info["user"]["real_name"]
            # Replace the mention with the user's name
            clean_text = clean_text.replace(f"<@{user_id}>", f"@{user_name}")
        except Exception as e:
            print(f"Error getting user info: {str(e)}")
            # If we can't get the user info, just remove the mention format
            clean_text = clean_text.replace(f"<@{user_id}>", f"@user")
    
    return clean_text

def submit_async_task(coroutine):
    """Submit an async task to the event loop"""
    global loop
    if loop is None or loop.is_closed():
        # Create a new event loop if needed
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Create a future in the event loop
    future = asyncio.run_coroutine_threadsafe(coroutine, loop)
    return future

# Example: Event listener for app mentions
@bolt_app.event("app_mention")
def handle_app_mention(event, say):
    user_text = event.get("text", "")
    clean_text = clean_user_text(user_text)
    
    print(f"[Slack] Incoming app_mention: {clean_text}")
    # Submit the async task to the event loop
    submit_async_task(process_slack_message_async(clean_text, say))

@bolt_app.event("message")
def handle_message(event, say):
    # Skip messages from bots
    if event.get("bot_id"):
        return
        
    # Skip messages in threads
    if event.get("thread_ts"):
        return
        
    user_text = event.get("text", "")
    clean_text = clean_user_text(user_text)
    
    print(f"[Slack] Incoming message: {clean_text}")
    # Submit the async task to the event loop
    submit_async_task(process_slack_message_async(clean_text, say))

# Flask endpoint for Slack events
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

# Flask root (optional)
@flask_app.route("/")
def index():
    return "Slack bot is running!"

def start_event_loop():
    """Start the event loop in a separate thread"""
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Run Flask app
if __name__ == "__main__":
    # Start the event loop in a separate thread
    loop_thread = threading.Thread(target=start_event_loop, daemon=True)
    loop_thread.start()
    
    # If using Socket Mode
    if SLACK_APP_TOKEN:
        socket_handler = SocketModeHandler(bolt_app, SLACK_APP_TOKEN)
        socket_handler.start()
    
    # Run Flask app
    flask_app.run(debug=True, port=5000)
