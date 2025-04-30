from agency_swarm.tools import BaseTool
from pydantic import Field
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# For a real implementation, this would connect to a database or user management system
# For this example, we'll simulate user status with shared state
class CheckUserStatus(BaseTool):
    """
    Checks the status of a user (online, offline, active, inactive).
    This tool retrieves the current status of a user to help determine
    how to handle their messages and responses.
    """
    
    user_id: str = Field(
        ..., description="Unique identifier for the user whose status is being checked."
    )

    def run(self):
        """
        Check the current status of the user.
        Returns information about whether the user is online/offline and active/inactive.
        """
        # In a real implementation, this would query a database or user management system
        # For this example, we'll use the shared state to track user activity
        
        # Get the last activity timestamp for the user
        last_activity_key = f"last_activity_{self.user_id}"
        last_activity = self._shared_state.get(last_activity_key)
        
        # Get the current time
        now = datetime.now()
        
        # Default status if user has no recorded activity
        if not last_activity:
            status = {
                "user_id": self.user_id,
                "online": False,
                "active": False,
                "last_active": None,
                "status_message": "User has no recorded activity"
            }
        else:
            # Parse the timestamp
            last_active_time = datetime.fromisoformat(last_activity["timestamp"])
            
            # Determine if the user is online (active in the last 5 minutes)
            online = now - last_active_time < timedelta(minutes=5)
            
            # Determine if the user is active (active in the last 15 minutes)
            active = now - last_active_time < timedelta(minutes=15)
            
            status = {
                "user_id": self.user_id,
                "online": online,
                "active": active,
                "last_active": last_activity["timestamp"],
                "status_message": "User is " + ("online" if online else "offline") + " and " + ("active" if active else "inactive")
            }
        
        return json.dumps(status)
    
    def _update_user_activity(self):
        """
        Update the user's last activity timestamp.
        This should be called whenever a user performs an action.
        """
        activity = {
            "timestamp": datetime.now().isoformat(),
            "user_id": self.user_id
        }
        self._shared_state.set(f"last_activity_{self.user_id}", activity)


if __name__ == "__main__":
    # Simulate user activity
    tool = CheckUserStatus(user_id="user123")
    
    # Update user activity (this would be called when a user performs an action)
    tool._update_user_activity()
    
    # Check user status
    result = tool.run()
    print("Initial status:", result)
    
    # Wait a moment and check again
    import time
    print("Waiting 2 seconds...")
    time.sleep(2)
    
    result = tool.run()
    print("Status after waiting:", result) 