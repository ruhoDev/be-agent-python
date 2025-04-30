from agency_swarm.tools import BaseTool
from pydantic import Field
import json
import re
from dotenv import load_dotenv

load_dotenv()

class CategorizeMessage(BaseTool):
    """
    Categorizes a message into predefined categories (question, statement, request, etc.).
    This tool determines the type of message to help generate appropriate responses.
    """
    
    message: str = Field(
        ..., description="The message text to categorize."
    )

    def run(self):
        """
        Categorize the message into predefined categories.
        Returns the primary and secondary categories of the message.
        """
        if not self.message.strip():
            return json.dumps({
                "status": "error",
                "message": "Message cannot be empty"
            })
            
        # In a production environment, you would use a proper NLP classifier
        # Here we'll use simple pattern matching to categorize the message
            
        # Define patterns for different categories
        patterns = {
            "question": [
                r'\bwho\b', r'\bwhat\b', r'\bwhen\b', r'\bwhere\b', r'\bwhy\b', r'\bhow\b',
                r'\bcan you\b', r'\bcould you\b', r'\bwould you\b', r'\?$'
            ],
            "greeting": [
                r'^hi\b', r'^hello\b', r'^hey\b', r'^good morning\b', r'^good afternoon\b',
                r'^good evening\b', r'^greetings\b', r'^howdy\b'
            ],
            "farewell": [
                r'\bbye\b', r'\bgoodbye\b', r'\bsee you\b', r'\btalk to you later\b',
                r'\btake care\b', r'\bhave a good day\b', r'\bhave a nice day\b'
            ],
            "gratitude": [
                r'\bthanks\b', r'\bthank you\b', r'\bappreciate\b', r'\bgrateful\b'
            ],
            "apology": [
                r'\bsorry\b', r'\bapologize\b', r'\bapologies\b', r'\bexcuse me\b',
                r'\bpardon\b', r'\bmy bad\b', r'\bmistake\b'
            ],
            "request": [
                r'\bcan you\b', r'\bcould you\b', r'\bwould you\b', r'\bplease\b',
                r'\bhelp me\b', r'\bI need\b', r'\bi want\b', r'\bassist\b'
            ],
            "complaint": [
                r'\bnot working\b', r'\bproblem\b', r'\bissue\b', r'\bcomplain\b',
                r'\bfail\b', r'\bbroken\b', r'\bdoesn\'t work\b', r'\bunable\b',
                r'\bdissatisfied\b', r'\bunhappy\b', r'\bfail\b', r'\bpoor\b'
            ],
            "feedback": [
                r'\bsuggestion\b', r'\bfeedback\b', r'\bimprove\b', r'\bimprovement\b',
                r'\benhance\b', r'\bbetter if\b', r'\bcould be better\b'
            ]
        }
        
        # Initialize category counts
        category_scores = {category: 0 for category in patterns}
        
        # Count pattern matches for each category
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, self.message.lower())
                category_scores[category] += len(matches)
        
        # Find the primary and secondary categories
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_category = sorted_categories[0][0] if sorted_categories[0][1] > 0 else "statement"
        secondary_category = sorted_categories[1][0] if len(sorted_categories) > 1 and sorted_categories[1][1] > 0 else None
        
        # If the message doesn't match any patterns, it's a general statement
        if primary_category == "statement" or sorted_categories[0][1] == 0:
            primary_category = "statement"
            # Check if it might be an introduction
            if re.search(r'\bmy name\b|\bi am\b|\bi\'m\b', self.message.lower()):
                secondary_category = "introduction"
        
        # Format the result
        result = {
            "primary_category": primary_category,
            "secondary_category": secondary_category,
            "category_scores": category_scores
        }
        
        return json.dumps(result)


if __name__ == "__main__":
    # Test with different messages
    test_messages = [
        "Can you help me find information about your services?",
        "Hello, how are you doing today?",
        "Thank you for your assistance with my order.",
        "The website is not working properly, I keep getting errors.",
        "I think it would be better if you added a search feature.",
        "My name is John and I'm new to your platform."
    ]
    
    for test_message in test_messages:
        tool = CategorizeMessage(message=test_message)
        result = tool.run()
        print(f"Message: '{test_message}'")
        print(f"Result: {result}\n") 