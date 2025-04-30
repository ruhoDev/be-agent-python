from agency_swarm.tools import BaseTool
from pydantic import Field
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ReceiveMessage(BaseTool):
    """
    Receives a message from the user and prepares it for processing.
    This tool handles the initial reception of user messages, validates them,
    and formats them for further processing by other agents.
    """
    
    message: str = Field(
        ..., description="The message content received from the user."
    )
    
    user_id: str = Field(
        ..., description="Unique identifier for the user sending the message."
    )

    def run(self):
        """
        Process the incoming message and prepare it for further handling.
        Validates that the message is not empty and formats it with metadata.
        """
        # Validate the message
        if not self.message.strip():
            return json.dumps({
                "status": "error",
                "message": "Message cannot be empty"
            })
            
        # Format the message with metadata
        formatted_message = {
            "user_id": self.user_id,
            "message": self.message,
            "timestamp": datetime.now().isoformat(),
            "message_id": f"{self.user_id}-{int(datetime.now().timestamp())}"
        }
        
        # Store in shared state for other agents to access
        self._shared_state.set(f"last_message_{self.user_id}", formatted_message)
        
        return json.dumps(formatted_message)


if __name__ == "__main__":
    # Test the tool
    tool = ReceiveMessage(message="Hello, how are you today?", user_id="user123")
    result = tool.run()
    print(result) 