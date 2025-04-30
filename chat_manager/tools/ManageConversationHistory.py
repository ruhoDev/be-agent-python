from agency_swarm.tools import BaseTool
from pydantic import Field
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ManageConversationHistory(BaseTool):
    """
    Manages the conversation history for each user.
    This tool handles storing, retrieving, and clearing conversation history
    to maintain context across multiple interactions.
    """
    
    user_id: str = Field(
        ..., description="Unique identifier for the user whose conversation history is being managed."
    )
    
    action: str = Field(
        ..., description="The action to perform: 'get' (retrieve history), 'add' (add message to history), or 'clear' (clear history)."
    )
    
    message: str = Field(
        None, description="The message to add to the history. Required only when action is 'add'."
    )
    
    role: str = Field(
        "user", description="The role of the message sender: 'user' or 'assistant'. Used only when action is 'add'."
    )

    def run(self):
        """
        Manage the conversation history based on the specified action.
        Can retrieve, add to, or clear the conversation history.
        """
        # Validate the action
        valid_actions = ["get", "add", "clear"]
        if self.action not in valid_actions:
            return json.dumps({
                "status": "error",
                "message": f"Invalid action. Must be one of: {', '.join(valid_actions)}"
            })
            
        # Get the current conversation history from shared state
        history_key = f"conversation_history_{self.user_id}"
        history = self._shared_state.get(history_key, [])
        
        # Perform the requested action
        if self.action == "get":
            return json.dumps({
                "status": "success",
                "history": history
            })
            
        elif self.action == "add":
            # Validate that a message is provided for the 'add' action
            if not self.message:
                return json.dumps({
                    "status": "error",
                    "message": "Message is required when action is 'add'"
                })
                
            # Add the message to the history
            history.append({
                "role": self.role,
                "content": self.message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Update the history in shared state
            self._shared_state.set(history_key, history)
            
            return json.dumps({
                "status": "success",
                "message": "Message added to history",
                "history_length": len(history)
            })
            
        elif self.action == "clear":
            # Clear the history
            self._shared_state.set(history_key, [])
            
            return json.dumps({
                "status": "success",
                "message": "Conversation history cleared"
            })


if __name__ == "__main__":
    # Test the tool - Add a message
    add_tool = ManageConversationHistory(
        user_id="user123",
        action="add",
        message="Hello, how can you help me today?",
        role="user"
    )
    add_result = add_tool.run()
    print("Add result:", add_result)
    
    # Test the tool - Get history
    get_tool = ManageConversationHistory(
        user_id="user123",
        action="get"
    )
    get_result = get_tool.run()
    print("Get result:", get_result)
    
    # Test the tool - Clear history
    clear_tool = ManageConversationHistory(
        user_id="user123",
        action="clear"
    )
    clear_result = clear_tool.run()
    print("Clear result:", clear_result) 