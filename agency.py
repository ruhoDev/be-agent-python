from agency_swarm import Agency
from chat_manager import ChatManager
from chat_processor import ChatProcessor
from chat_assistant import ChatAssistant
from dotenv import load_dotenv

load_dotenv()

# Initialize the agents
chat_manager = ChatManager()
chat_processor = ChatProcessor()
chat_assistant = ChatAssistant()

# Define the agency with communication flows and enable async mode
agency = Agency(
    [
        chat_manager,  # Chat Manager will be the entry point for communication with the user
        [chat_manager, chat_processor],  # Chat Manager can communicate with Chat Processor
        [chat_processor, chat_assistant],  # Chat Processor can communicate with Chat Assistant
        [chat_assistant, chat_manager],  # Chat Assistant can communicate with Chat Manager
    ],
    shared_instructions="agency_manifesto.md",  # Shared instructions for all agents
    temperature=0.4,  # Default temperature for all agents
    max_prompt_tokens=25000,  # Default max tokens in conversation history
    async_mode="threading"  # Enable async mode with asyncio instead of threading
)

if __name__ == "__main__":
    agency.demo_gradio()
    agency.run_demo()  # Run the agency in terminal demo mode
