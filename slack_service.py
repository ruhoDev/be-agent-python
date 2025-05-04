from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from firebase_service import FirebaseService
import os
from dotenv import load_dotenv
import threading
import time

load_dotenv()

class SlackService:
    """Service for managing Slack bot configurations and connections"""
    
    _instance = None
    _bots = {}  # Dictionary to store bot instances by ID
    _handlers = {}  # Dictionary to store request handlers by ID
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SlackService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the Slack service"""
        # Initialize Firebase service
        self.firebase = FirebaseService()
        
        # Start background thread for bot refreshing
        self._stop_refresh = False
        self._refresh_thread = threading.Thread(target=self._background_refresh, daemon=True)
        self._refresh_thread.start()
    
    def get_bot_app(self, bot_id: str):
        """
        Get a Slack app instance for a specific bot
        
        Args:
            bot_id: The ID of the Slack bot
            
        Returns:
            Tuple of (Slack App instance, SlackRequestHandler)
        """
        # Check if we already have this bot initialized
        if bot_id in self._bots:
            return self._bots[bot_id], self._handlers[bot_id]
        
        # Fetch bot configuration from Firebase
        bot_config = self.firebase.get_slack_bot(bot_id)
        if not bot_config:
            print(f"Error: No bot configuration found for ID {bot_id}")
            return None, None
        
        # Initialize new Slack app with bot configuration
        bot_token = bot_config.get('bot_token')
        signing_secret = bot_config.get('signing_secret')
        
        if not bot_token or not signing_secret:
            print(f"Error: Missing bot token or signing secret for bot ID {bot_id}")
            return None, None
        
        try:
            # Create new Slack app instance
            app = App(token=bot_token, signing_secret=signing_secret)
            handler = SlackRequestHandler(app)
            
            # Store in cache
            self._bots[bot_id] = app
            self._handlers[bot_id] = handler
            
            return app, handler
        except Exception as e:
            print(f"Error creating Slack app for bot ID {bot_id}: {str(e)}")
            return None, None
    
    def get_agent_for_bot(self, bot_id: str):
        """
        Get the agent configuration for a specific bot
        
        Args:
            bot_id: The ID of the Slack bot
            
        Returns:
            Agent configuration dictionary or None if not found
        """
        # Fetch bot configuration from Firebase
        bot_config = self.firebase.get_slack_bot(bot_id)
        if not bot_config:
            print(f"Error: No bot configuration found for ID {bot_id}")
            return None
        
        # Get agent ID from bot configuration
        agent_id = bot_config.get('agent_id')
        if not agent_id:
            print(f"Error: No agent ID found for bot ID {bot_id}")
            return None
        
        # Fetch agent configuration from Firebase
        return self.firebase.get_agent(agent_id)
    
    def get_all_active_bots(self):
        """
        Get all active bots from Firebase
        
        Returns:
            List of bot configuration dictionaries
        """
        return self.firebase.get_active_slack_bots()
    
    def _background_refresh(self):
        """Background thread to refresh bot configurations periodically"""
        while not self._stop_refresh:
            # Sleep for 5 minutes
            time.sleep(300)
            
            # Refresh all bot configurations
            try:
                active_bots = self.get_all_active_bots()
                for bot in active_bots:
                    bot_id = bot.get('agent_id')  # Assuming agent_id is the document ID
                    if bot_id in self._bots:
                        # Update the bot configuration
                        bot_token = bot.get('bot_token')
                        signing_secret = bot.get('signing_secret')
                        
                        if bot_token and signing_secret:
                            # Recreate the bot app with updated configuration
                            app = App(token=bot_token, signing_secret=signing_secret)
                            handler = SlackRequestHandler(app)
                            
                            # Update cache
                            self._bots[bot_id] = app
                            self._handlers[bot_id] = handler
            except Exception as e:
                print(f"Error in background refresh: {str(e)}")
    
    def shutdown(self):
        """Shut down the service and stop the background thread"""
        self._stop_refresh = True
        if self._refresh_thread.is_alive():
            self._refresh_thread.join(timeout=1.0)


# Example usage
if __name__ == "__main__":
    # Initialize Slack service
    slack_service = SlackService()
    
    # Get a specific bot
    bot_id = "v5xVoUOyqKySIv3trXWv"  # Replace with actual bot ID
    slack_app, handler = slack_service.get_bot_app(bot_id)
    
    if slack_app:
        print(f"Successfully initialized Slack app for bot ID {bot_id}")
        
        # Get associated agent
        agent = slack_service.get_agent_for_bot(bot_id)
        if agent:
            print(f"Agent Name: {agent.get('name')}")
            print(f"Agent Model: {agent.get('model')}")
            print(f"Agent Temperature: {agent.get('temperature')}")
        else:
            print(f"No agent found for bot ID {bot_id}")
    else:
        print(f"Failed to initialize Slack app for bot ID {bot_id}") 