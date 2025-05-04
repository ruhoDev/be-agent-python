import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from typing import Dict, Any, Optional

class FirebaseService:
    """Service for interacting with Firebase Firestore"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Firebase with admin credentials"""
        if not FirebaseService._initialized:
            try:
                # Path to the Firebase Admin SDK credentials file
                cred_path = os.path.join(os.path.dirname(__file__), 
                                       'enabled-prototype-firebase-adminsdk-fbsvc-9011d71d18.json')
                
                # Initialize Firebase Admin SDK with credentials
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                
                # Get Firestore client
                self.db = firestore.client()
                FirebaseService._initialized = True
                print("Firebase Firestore initialized successfully")
            except Exception as e:
                print(f"Error initializing Firebase: {str(e)}")
                raise
    
    def get_slack_bot(self, bot_id: str) -> Optional[Dict[str, Any]]:
        """
        Get Slack bot details from Firestore
        
        Args:
            bot_id: The ID of the Slack bot to retrieve
            
        Returns:
            Dictionary containing bot details or None if not found
        """
        try:
            doc_ref = self.db.collection('slack_bots').document(bot_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                print(f"No slack bot found with ID: {bot_id}")
                return None
        except Exception as e:
            print(f"Error retrieving slack bot: {str(e)}")
            return None
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent details from Firestore
        
        Args:
            agent_id: The ID of the agent to retrieve
            
        Returns:
            Dictionary containing agent details or None if not found
        """
        try:
            doc_ref = self.db.collection('agents').document(agent_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                print(f"No agent found with ID: {agent_id}")
                return None
        except Exception as e:
            print(f"Error retrieving agent: {str(e)}")
            return None
    
    def get_slack_bots_by_user(self, user_id: str) -> list:
        """
        Get all Slack bots associated with a specific user
        
        Args:
            user_id: The user ID to find bots for
            
        Returns:
            List of bot dictionaries
        """
        try:
            bots_ref = self.db.collection('slack_bots').where('user_id', '==', user_id)
            bots = bots_ref.stream()
            
            return [bot.to_dict() for bot in bots]
        except Exception as e:
            print(f"Error retrieving slack bots for user: {str(e)}")
            return []

    def get_active_slack_bots(self) -> list:
        """
        Get all active Slack bots from Firestore
        
        Returns:
            List of bot dictionaries
        """
        try:
            bots_ref = self.db.collection('slack_bots').where('is_active', '==', True)
            bots = bots_ref.stream()
            
            return [bot.to_dict() for bot in bots]
        except Exception as e:
            print(f"Error retrieving active slack bots: {str(e)}")
            return []


# Example usage
if __name__ == "__main__":
    # Initialize Firebase service
    firebase_service = FirebaseService()
    
    # Example: Get a Slack bot by ID
    bot_id = "v5xVoUOyqKySIv3trXWv"  # Replace with actual bot ID
    slack_bot = firebase_service.get_slack_bot(bot_id)
    
    if slack_bot:
        print(f"Bot Name: {slack_bot.get('name')}")
        print(f"Bot Token: {slack_bot.get('bot_token')}")
        print(f"Signing Secret: {slack_bot.get('signing_secret')}")
        
        # Get associated agent
        agent_id = slack_bot.get('agent_id')
        if agent_id:
            agent = firebase_service.get_agent(agent_id)
            if agent:
                print(f"\nAssociated Agent: {agent.get('name')}")
                print(f"Agent Model: {agent.get('model')}")
                print(f"Agent Instructions: {agent.get('instructions')[:100]}...")
            else:
                print(f"Associated agent not found with ID: {agent_id}")
    else:
        print(f"Slack bot not found with ID: {bot_id}") 