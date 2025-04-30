from agency_swarm.tools import BaseTool
from pydantic import Field
import json
import re
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

class ExtractKeywords(BaseTool):
    """
    Extracts key topics and keywords from a message.
    This tool identifies the most important words and phrases in a message
    to help understand the main topics and user intent.
    """
    
    message: str = Field(
        ..., description="The message text to extract keywords from."
    )
    
    max_keywords: int = Field(
        5, description="The maximum number of keywords to extract."
    )

    def run(self):
        """
        Extract keywords and key phrases from the provided message.
        Returns a list of the most important words and phrases.
        """
        if not self.message.strip():
            return json.dumps({
                "status": "error",
                "message": "Message cannot be empty"
            })
            
        # In a production environment, you would use a proper NLP library or API
        # such as NLTK, spaCy, KeyBERT, or a cloud-based keyword extraction service
        # For this example, we'll use a simple frequency-based approach with stopword filtering
        
        # Convert to lowercase
        text = self.message.lower()
        
        # Remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        
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
        
        # Count word frequencies
        word_counts = Counter(words)
        
        # Get the most common words
        keywords = [word for word, count in word_counts.most_common(self.max_keywords)]
        
        # Look for bigrams (two-word phrases) that might be important
        if len(words) > 1:
            bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
            bigram_counts = Counter(bigrams)
            
            # Add top bigrams to keywords if they appear frequently
            for bigram, count in bigram_counts.most_common(3):
                if count > 1 and len(keywords) < self.max_keywords:
                    keywords.append(bigram)
        
        # Format the result
        result = {
            "keywords": keywords,
            "keyword_count": len(keywords),
            "message_word_count": len(text.split())
        }
        
        return json.dumps(result)


if __name__ == "__main__":
    # Test with different messages
    test_messages = [
        "I need help with my account settings, I can't find where to change my password.",
        "What are your business hours on weekends and holidays?",
        "The new smartphone has an amazing camera and battery life.",
        "Can you recommend a good restaurant in downtown?"
    ]
    
    for test_message in test_messages:
        tool = ExtractKeywords(message=test_message)
        result = tool.run()
        print(f"Message: '{test_message}'")
        print(f"Result: {result}\n") 