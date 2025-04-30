from agency_swarm.tools import BaseTool
from pydantic import Field
import json
import re
from dotenv import load_dotenv

load_dotenv()

class AnalyzeSentiment(BaseTool):
    """
    Analyzes the sentiment of a message (positive, negative, neutral).
    This tool determines the emotional tone of a message to help generate
    appropriate responses.
    """
    
    message: str = Field(
        ..., description="The message text to analyze for sentiment."
    )

    def run(self):
        """
        Analyze the sentiment of the provided message.
        Returns a sentiment classification and confidence score.
        """
        # In a production environment, you would use a proper NLP library or API
        # such as NLTK, TextBlob, spaCy, or a cloud-based sentiment analysis service
        # For this example, we'll use a simple keyword-based approach
        
        if not self.message.strip():
            return json.dumps({
                "status": "error",
                "message": "Message cannot be empty"
            })
            
        # Simple sentiment analysis using keyword matching
        positive_words = [
            r'\bgood\b', r'\bgreat\b', r'\bamazing\b', r'\bawesome\b', r'\bhappy\b',
            r'\bexcellent\b', r'\blove\b', r'\bthank\b', r'\bthanks\b', r'\bappreciate\b',
            r'\bpositive\b', r'\bexcited\b', r'\bglad\b', r'\bnice\b', r'\bpleasant\b',
            r'\bwonderful\b', r'\bjoy\b', r'\bimpressive\b', r'\bimpressed\b'
        ]
        
        negative_words = [
            r'\bbad\b', r'\bterrible\b', r'\bhorrible\b', r'\bawful\b', r'\bsad\b',
            r'\bunhappy\b', r'\bangry\b', r'\bupset\b', r'\bdisappointed\b', r'\bfail\b',
            r'\bpoor\b', r'\bnegative\b', r'\bunfortunate\b', r'\bsorry\b', r'\bmistake\b',
            r'\bworst\b', r'\bhate\b', r'\btrouble\b', r'\binconvenient\b', r'\bproblem\b'
        ]
        
        # Count occurrences of positive and negative words
        positive_count = sum(len(re.findall(word, self.message.lower())) for word in positive_words)
        negative_count = sum(len(re.findall(word, self.message.lower())) for word in negative_words)
        
        # Determine the overall sentiment
        if positive_count > negative_count:
            sentiment = "positive"
            score = min(1.0, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            score = min(1.0, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            # Check for question marks as an indication of a question rather than neutral statement
            if '?' in self.message:
                sentiment = "question"
                score = 0.7
            else:
                sentiment = "neutral"
                score = 0.5
        
        # Format the result
        result = {
            "sentiment": sentiment,
            "score": round(score, 2),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "message_length": len(self.message)
        }
        
        return json.dumps(result)


if __name__ == "__main__":
    # Test with different messages
    test_messages = [
        "I'm really happy with the service you provided, it was excellent!",
        "This is terrible, I'm very disappointed with the quality.",
        "Can you tell me more about your products?",
        "The weather is cloudy today."
    ]
    
    for test_message in test_messages:
        tool = AnalyzeSentiment(message=test_message)
        result = tool.run()
        print(f"Message: '{test_message}'")
        print(f"Result: {result}\n") 