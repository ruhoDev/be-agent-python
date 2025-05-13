from agency_swarm import Agency
from agency_swarm import Agent
from dotenv import load_dotenv
from firebase_service import FirebaseService
import os

load_dotenv()

# Initialize Firebase service for conversation storage
firebase_service = FirebaseService()

def get_threads_from_db(conversation_id):
    """
    Load conversation threads from Firestore database
    
    Args:
        conversation_id: Unique identifier for the conversation (channel:thread_id)
        
    Returns:
        Dictionary of conversation threads or empty dict if not found
    """
    try:
        doc = firebase_service.db.collection('slack_conversations').document(conversation_id).get()
        if doc.exists:
            return doc.to_dict().get('threads', {})
        else:
            return {}
    except Exception as e:
        print(f"Error loading threads from database: {str(e)}")
        return {}

def save_threads_to_db(conversation_id, threads):
    """
    Save conversation threads to Firestore database
    
    Args:
        conversation_id: Unique identifier for the conversation (channel:thread_id)
        threads: Dictionary of conversation threads to save
    """
    try:
        firebase_service.db.collection('slack_conversations').document(conversation_id).set({
            'threads': threads
        })
    except Exception as e:
        print(f"Error saving threads to database: {str(e)}")

def generate_response(message, conversation_id=None, agent_config=None):
    """
    Generate a response from the agency
    
    Args:
        message: The user message to process
        conversation_id: Optional unique identifier for the conversation (channel:thread_id)
        agent_config: Optional agent configuration to customize response parameters
        
    Returns:
        Generated response from the agency
    """
    agents = []

    # If conversation_id is provided, use thread persistence
    if conversation_id and agent_config:
        agent = Agent(
            name=agent_config.get('name', 'Assistant'),
            description=agent_config.get('description', ''),
            instructions=agent_config.get('instructions', ''),
            temperature=agent_config.get('temperature', 0.4),
            max_prompt_tokens=agent_config.get('max_tokens', 25000),
            # model=agent_config.get('model', 'gpt-4o-mini')
        )
        agents.append(agent)

    # If no agents were configured, use a default agent
    if not agents:
        default_agent = Agent(
            name="Assistant",
            description="A helpful AI assistant",
            instructions="You are a helpful AI assistant that provides accurate and concise responses.",
            temperature=0.4,
            max_prompt_tokens=25000
        )
        agents.append(default_agent)
    
    # Create a new agency instance with thread persistence
    agency = Agency(
        agents,
        temperature=agent_config.get('temperature', 0.4) if agent_config else 0.4,
        max_prompt_tokens=agent_config.get('max_tokens', 25000) if agent_config else 25000,
        # model=agent_config.get('model', 'gpt-4o-mini') if agent_config else 'gpt-4o-mini',
        threads_callbacks={
            "load": lambda: get_threads_from_db(conversation_id),
            "save": lambda threads: save_threads_to_db(conversation_id, threads),
        }
    )
        
    # Get completion from the temporary agency
    completion = agency.get_completion(message, yield_messages=False)
    print('completion', completion)
    return completion