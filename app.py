from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import asyncio
import re
import concurrent.futures
from functools import partial
from agency import agency
import threading
import atexit

# Import custom utilities
from utils import logger, error_handler, async_manager, config

# Initialize logging
log = logger.get_logger(__name__)

# Load configuration
load_dotenv()
app_config = config.AppConfig.from_env()

# Initialize the Slack app if credentials are available
bolt_app = None
handler = None
if app_config.slack.is_configured:
    log.info("Initializing Slack app with provided credentials")
    bolt_app = App(token=app_config.slack.bot_token, signing_secret=app_config.slack.signing_secret)
    flask_app = Flask(__name__)
    handler = SlackRequestHandler(bolt_app)
else:
    log.warning("Slack credentials not found, Slack integration will be disabled")
    flask_app = Flask(__name__)

# Thread pool for running synchronous agency methods
executor = concurrent.futures.ThreadPoolExecutor(max_workers=app_config.async_config.max_workers)
log.info(f"Initialized thread pool with {app_config.async_config.max_workers} workers")

# Event loop for async operations
loop = None

@error_handler.async_handle_errors
async def process_message_async(text):
    """Process a message through the agency asynchronously"""
    try:
        # Run agency with timeout protection
        timeout = app_config.async_config.task_timeout
        log.info(f"Processing message with timeout {timeout}s: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        result = await asyncio.wait_for(
            async_get_completion(text), 
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        log.warning(f"Message processing timed out after {timeout}s")
        return "⏱️ The response timed out. Please try a shorter or simpler query."
    except Exception as e:
        log.error(f"Error processing message: {str(e)}", exc_info=True)
        error_id = error_handler.generate_error_id()
        error_handler.report_error(error_id, e)
        return error_handler.format_error_for_user(e)

async def async_get_completion(text):
    """Wrapper to make synchronous get_completion work asynchronously"""
    loop = asyncio.get_running_loop()
    # Run the synchronous method in a thread pool
    return await loop.run_in_executor(
        executor,  # Use our thread pool
        lambda: agency.get_completion(text, yield_messages=False)
    )

@error_handler.async_handle_errors
async def process_slack_message_async(text, say):
    """Handle Slack messages by processing them through the agency asynchronously"""
    # Set request context for logging
    request_id = logger.set_request_context()
    log.info(f"[Slack] Processing: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    try:
        # Process the message asynchronously
        result = await process_message_async(text)
        log.info(f"[Slack] Result generated successfully")
        say(result)
    except Exception as e:
        error_id = error_handler.generate_error_id()
        log.error(f"[Slack] Error: {str(e)}", exc_info=True, extra={"error_id": error_id})
        error_msg = error_handler.format_error_for_user(e)
        say(error_msg)

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

def submit_async_task(coroutine, task_name=None):
    """Submit an async task to the event loop"""
    # Use the improved async manager
    return async_manager.submit_async_task(coroutine, task_name)

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
    # Use the improved async manager
    async_manager.start_async_manager()

# Add API endpoint for direct chat
@flask_app.route("/api/chat", methods=["POST"])
def api_chat():
    """Direct API endpoint for chat without Slack"""
    # Set request context
    request_id = logger.set_request_context()
    
    try:
        # Get request data
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Extract message
        message = data.get("message")
        if not message:
            return jsonify({"error": "No message provided"}), 400
            
        log.info(f"API chat request: {message[:50]}{'...' if len(message) > 50 else ''}")
        
        # Process the message
        result = agency.generate_response(message)
        
        # Return the response
        return jsonify({
            "response": result,
            "request_id": request_id
        })
    except Exception as e:
        error_id = error_handler.generate_error_id()
        log.error(
            f"Error in API chat: {str(e)}",
            exc_info=True, 
            extra={"error_id": error_id, "request_id": request_id}
        )
        
        return jsonify({
            "error": str(e),
            "error_id": error_id
        }), 500

# Add health check endpoint
@flask_app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "slack_configured": app_config.slack.is_configured,
        "openai_configured": app_config.openai.is_configured
    })

# Graceful shutdown
def shutdown_handler():
    """Handle graceful shutdown"""
    log.info("Shutting down application")
    
    # Shutdown async manager
    async_manager.shutdown_async_manager()
    
    # Shutdown thread pool
    executor.shutdown(wait=False)
    
    log.info("Application shutdown complete")

# Run Flask app
if __name__ == "__main__":
    try:
        # Configure logging
        log.info("Starting Simple Chat Agency application")
        
        # Start the event loop in a separate thread
        start_event_loop()
        log.info("Event loop started")
        
        # Register shutdown handler
        atexit.register(shutdown_handler)
        
        # If using Socket Mode and Slack is configured
        if app_config.slack.app_token and bolt_app:
            log.info("Starting Slack socket mode handler")
            socket_handler = SocketModeHandler(
                bolt_app, 
                app_config.slack.app_token
            )
            socket_handler.start()
        
        # Run Flask app
        log.info(f"Starting Flask app on {app_config.flask.host}:{app_config.flask.port}")
        flask_app.run(
            debug=app_config.flask.debug,
            port=app_config.flask.port,
            host=app_config.flask.host
        )
    except Exception as e:
        log.critical(f"Failed to start application: {str(e)}", exc_info=True)
        raise
