from agency_swarm.tools import BaseTool
from pydantic import Field
import json
from dotenv import load_dotenv

load_dotenv()

class GenerateResponse(BaseTool):
    """
    Generates a response to a user's message based on the context and intent.
    This tool creates appropriate, contextually relevant responses to user messages
    using the analysis provided by the Chat Processor.
    """
    
    message: str = Field(
        ..., description="The original user message."
    )
    
    sentiment: str = Field(
        None, description="The sentiment of the message (positive, negative, neutral, question)."
    )
    
    category: str = Field(
        None, description="The category of the message (question, greeting, request, etc.)."
    )
    
    keywords: list = Field(
        None, description="List of keywords from the message."
    )
    
    user_id: str = Field(
        ..., description="Unique identifier for the user."
    )

    def run(self):
        """
        Generate a contextually appropriate response to the user's message.
        Uses the message content, sentiment, category, and keywords to craft a response.
        """
        if not self.message.strip():
            return json.dumps({
                "status": "error",
                "message": "Message cannot be empty"
            })
            
        # Get conversation history if available
        history_key = f"conversation_history_{self.user_id}"
        history = self._shared_state.get(history_key, [])
        
        # Use the sentiment, category, and keywords to craft an appropriate response
        # In a production system, this would likely use a more sophisticated approach
        
        # Parse sentiment, category, and keywords if they're in JSON format
        sentiment = self._parse_json_or_text(self.sentiment)
        if isinstance(sentiment, dict) and "sentiment" in sentiment:
            sentiment = sentiment["sentiment"]
        
        category = self._parse_json_or_text(self.category)
        if isinstance(category, dict) and "primary_category" in category:
            category = category["primary_category"]
            
        keywords = self._parse_json_or_text(self.keywords)
        if isinstance(keywords, dict) and "keywords" in keywords:
            keywords = keywords["keywords"]
            
        # Generate response based on message category
        if category == "greeting":
            response = self._handle_greeting(history)
        elif category == "farewell":
            response = self._handle_farewell()
        elif category == "gratitude":
            response = self._handle_gratitude()
        elif category == "apology":
            response = "No problem at all. How can I assist you today?"
        elif category == "question":
            response = self._handle_question(self.message, keywords)
        elif category == "request":
            response = self._handle_request(self.message, keywords)
        elif category == "complaint":
            response = self._handle_complaint(sentiment)
        elif category == "feedback":
            response = "Thank you for your feedback! We're always looking to improve our services."
        else:  # Default/statement
            response = self._handle_statement(self.message, sentiment)
            
        # Store the response in shared state
        self._shared_state.set(f"last_generated_response_{self.user_id}", response)
        
        return response
    
    def _parse_json_or_text(self, value):
        """Helper method to parse a value that might be JSON or plain text."""
        if not value:
            return None
            
        if isinstance(value, list) or isinstance(value, dict):
            return value
            
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def _handle_greeting(self, history):
        """Generate an appropriate greeting response."""
        if not history:
            return "Hello! Welcome to our chat service. How can I assist you today?"
        else:
            return "Hello again! How can I help you today?"
    
    def _handle_farewell(self):
        """Generate an appropriate farewell response."""
        return "Thank you for chatting with us today. Have a great day!"
    
    def _handle_gratitude(self):
        """Generate an appropriate response to gratitude."""
        return "You're welcome! Is there anything else I can help you with?"
    
    def _handle_question(self, message, keywords):
        """Generate a response to a question."""
        # This would normally use more sophisticated logic or external APIs
        if keywords and any(keyword in ["hours", "open", "schedule", "time"] for keyword in keywords):
            return "We're open Monday through Friday from 9am to 5pm."
        elif keywords and any(keyword in ["location", "address", "where"] for keyword in keywords):
            return "Our main office is located at 123 Main Street, Suite 200, Anytown, USA."
        elif keywords and any(keyword in ["price", "cost", "pricing", "fee"] for keyword in keywords):
            return "Our pricing varies based on the specific service you're interested in. Could you please specify which service you'd like to know about?"
        else:
            return "That's a great question. Could you provide a bit more detail so I can give you a more accurate answer?"
    
    def _handle_request(self, message, keywords):
        """Generate a response to a request."""
        if keywords and any(keyword in ["help", "assist", "support"] for keyword in keywords):
            return "I'd be happy to help you. What specifically do you need assistance with?"
        else:
            return "I'll help you with that request. Could you provide a bit more information so I can assist you better?"
    
    def _handle_complaint(self, sentiment):
        """Generate a response to a complaint."""
        if sentiment == "negative":
            return "I'm very sorry to hear about your experience. I'll do my best to help resolve this issue for you. Could you please provide more details about what happened?"
        else:
            return "I understand your concern. Let me see how I can help address this issue."
    
    def _handle_statement(self, message, sentiment):
        """Generate a response to a general statement."""
        if sentiment == "positive":
            return "That's great to hear! Is there anything specific I can help you with today?"
        elif sentiment == "negative":
            return "I'm sorry to hear that. Is there anything I can do to help improve the situation?"
        else:
            return "I understand. Is there anything specific you'd like to know or discuss?"


if __name__ == "__main__":
    # Test with different scenarios
    test_cases = [
        {
            "message": "Hello there!",
            "sentiment": json.dumps({"sentiment": "positive", "score": 0.8}),
            "category": json.dumps({"primary_category": "greeting"}),
            "keywords": json.dumps({"keywords": ["hello"]}),
            "user_id": "user123"
        },
        {
            "message": "What are your business hours?",
            "sentiment": json.dumps({"sentiment": "neutral", "score": 0.5}),
            "category": json.dumps({"primary_category": "question"}),
            "keywords": json.dumps({"keywords": ["business", "hours"]}),
            "user_id": "user123"
        },
        {
            "message": "I'm having a problem with your website.",
            "sentiment": json.dumps({"sentiment": "negative", "score": 0.7}),
            "category": json.dumps({"primary_category": "complaint"}),
            "keywords": json.dumps({"keywords": ["problem", "website"]}),
            "user_id": "user123"
        }
    ]
    
    for test_case in test_cases:
        tool = GenerateResponse(**test_case)
        result = tool.run()
        print(f"Message: '{test_case['message']}'")
        print(f"Response: '{result}'\n") 