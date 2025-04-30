from agency_swarm.tools import BaseTool
from pydantic import Field
import json
import re
from dotenv import load_dotenv

load_dotenv()

class GenerateSuggestions(BaseTool):
    """
    Generates suggested replies or next steps for the user.
    This tool creates contextually relevant suggestions to help guide
    the conversation and provide quick response options.
    """
    
    context: str = Field(
        ..., description="The current conversation context or latest message."
    )
    
    count: int = Field(
        3, description="Number of suggestions to generate."
    )
    
    user_id: str = Field(
        None, description="Unique identifier for the user. If provided, conversation history will be used for better suggestions."
    )

    def run(self):
        """
        Generate suggested replies based on the conversation context.
        Returns a list of suggested replies the user might want to use next.
        """
        if not self.context.strip():
            return json.dumps({
                "status": "error",
                "message": "Context cannot be empty"
            })
            
        if self.count <= 0:
            return json.dumps({
                "status": "error",
                "message": "Count must be greater than 0"
            })
            
        # Get conversation history if user_id is provided
        history = []
        if self.user_id:
            history_key = f"conversation_history_{self.user_id}"
            history = self._shared_state.get(history_key, [])
            
        # In a production environment, this would use a more sophisticated model
        # to generate contextually relevant suggestions based on the conversation history
        # For this example, we'll use a rule-based approach to generate suggestions
        
        # Extract keywords from the context
        keywords = self._extract_keywords(self.context)
        
        # Generate suggestions based on the context and extracted keywords
        suggestions = self._generate_suggestions_from_context(self.context, keywords, history)
        
        # Limit to the requested count
        suggestions = suggestions[:self.count]
        
        return json.dumps({
            "status": "success",
            "suggestions": suggestions,
            "count": len(suggestions)
        })
    
    def _extract_keywords(self, text):
        """Extract keywords from the text."""
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Define stopwords (common words that don't carry much meaning)
        stopwords = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 
            'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 
            'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 
            'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 
            'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 
            'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 
            'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 
            'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 
            'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 
            'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 
            'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 
            'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 
            'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
        }
        
        # Split into words and filter out stopwords
        words = [word for word in text.split() if word not in stopwords and len(word) > 2]
        
        return words
    
    def _generate_suggestions_from_context(self, context, keywords, history):
        """Generate suggestions based on the context, keywords, and conversation history."""
        suggestions = []
        
        # Check for question marks in the context (indicating a question)
        if '?' in context:
            # Suggest responses to questions
            suggestions.extend([
                "Yes, that sounds good.",
                "No, I prefer something else.",
                "Can you provide more details?",
                "I'm not sure about that."
            ])
        
        # Check for greeting-related keywords
        if any(word in context.lower() for word in ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']):
            suggestions.extend([
                "Hello! How can I help you today?",
                "Hi there! What can I assist you with?",
                "I have a question about your services."
            ])
            
        # Check for product or service-related keywords
        if any(word in keywords for word in ['product', 'service', 'price', 'cost', 'purchase', 'buy']):
            suggestions.extend([
                "Can you tell me more about your pricing?",
                "What features does this product have?",
                "Do you offer any discounts?",
                "How can I make a purchase?"
            ])
            
        # Check for support-related keywords
        if any(word in keywords for word in ['help', 'support', 'issue', 'problem', 'error', 'trouble']):
            suggestions.extend([
                "I need help with a specific issue.",
                "Can you guide me through troubleshooting?",
                "Is there a knowledge base I can refer to?",
                "Can I speak with a support agent?"
            ])
            
        # Check for information-seeking keywords
        if any(word in keywords for word in ['information', 'details', 'learn', 'know', 'understand']):
            suggestions.extend([
                "Where can I find more information?",
                "Can you send me detailed documentation?",
                "I'd like to learn more about this topic.",
                "Can you explain this in simpler terms?"
            ])
            
        # Add some general suggestions if we don't have many specific ones
        if len(suggestions) < self.count:
            general_suggestions = [
                "Thank you for the information.",
                "I understand now.",
                "Could you elaborate on that?",
                "That's interesting, tell me more.",
                "What do you recommend?",
                "Is there anything else I should know?",
                "How do I get started?",
                "What are the next steps?"
            ]
            suggestions.extend(general_suggestions)
            
        # Deduplicate suggestions
        suggestions = list(dict.fromkeys(suggestions))
        
        return suggestions


if __name__ == "__main__":
    # Test with different contexts
    test_contexts = [
        "Hello, I'm interested in learning more about your services.",
        "What is the price of your premium package?",
        "I'm having trouble logging into my account. Can you help?",
        "Thanks for the information. I'll think about it.",
        "Can you explain how this product works?"
    ]
    
    for context in test_contexts:
        tool = GenerateSuggestions(context=context, count=3)
        result = tool.run()
        print(f"Context: '{context}'")
        print(f"Result: {result}\n") 