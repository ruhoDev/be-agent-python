from agency_swarm.tools import BaseTool
from pydantic import Field
import json
import re
from dotenv import load_dotenv

load_dotenv()

class DetectLanguage(BaseTool):
    """
    Detects the language of a message.
    This tool identifies the language of the text to help determine
    if translation is needed or to customize responses.
    """
    
    message: str = Field(
        ..., description="The message text to detect the language of."
    )

    def run(self):
        """
        Detect the language of the provided message.
        Returns the detected language code and confidence score.
        """
        if not self.message.strip():
            return json.dumps({
                "status": "error",
                "message": "Message cannot be empty"
            })
            
        # In a production environment, you would use a proper language detection library
        # such as langdetect, langid, or a cloud-based language detection service
        # For this example, we'll implement a simple language detection based on common words
            
        # Dictionary of language codes and their common words/patterns
        language_patterns = {
            "en": {  # English
                "words": ["the", "and", "is", "in", "to", "it", "you", "that", "was", "for", "on", "are", "with", "as", "they"],
                "patterns": [r"\bthe\b", r"\band\b", r"\bis\b", r"\bin\b", r"\bto\b", r"\bit\b", r"\byou\b", r"\bthat\b"]
            },
            "es": {  # Spanish
                "words": ["el", "la", "de", "en", "y", "a", "que", "los", "se", "un", "por", "con", "para", "es", "su"],
                "patterns": [r"\bel\b", r"\bla\b", r"\bde\b", r"\ben\b", r"\by\b", r"\ba\b", r"\bque\b", r"\blos\b"]
            },
            "fr": {  # French
                "words": ["le", "la", "de", "et", "à", "en", "un", "une", "du", "que", "qui", "dans", "les", "est", "pour"],
                "patterns": [r"\ble\b", r"\bla\b", r"\bde\b", r"\bet\b", r"\bà\b", r"\ben\b", r"\bun\b", r"\bune\b"]
            },
            "de": {  # German
                "words": ["der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich", "des", "auf", "für", "ist", "im"],
                "patterns": [r"\bder\b", r"\bdie\b", r"\bund\b", r"\bin\b", r"\bden\b", r"\bvon\b", r"\bzu\b", r"\bdas\b"]
            },
            "it": {  # Italian
                "words": ["il", "di", "che", "la", "in", "e", "per", "un", "una", "sono", "mi", "ho", "si", "lo", "non"],
                "patterns": [r"\bil\b", r"\bdi\b", r"\bche\b", r"\bla\b", r"\bin\b", r"\be\b", r"\bper\b", r"\bun\b"]
            }
        }
        
        # Normalize text for comparison
        text = self.message.lower()
        
        # Count matches for each language
        language_scores = {}
        
        for lang_code, patterns in language_patterns.items():
            score = 0
            
            # Check for word matches
            words = re.findall(r'\b\w+\b', text)
            for word in words:
                if word in patterns["words"]:
                    score += 1
            
            # Check for pattern matches
            for pattern in patterns["patterns"]:
                matches = re.findall(pattern, text)
                score += len(matches)
            
            # Normalize by the number of words to avoid bias toward longer texts
            language_scores[lang_code] = score / max(1, len(words))
        
        # Determine the most likely language
        if not language_scores:
            detected_language = "unknown"
            confidence = 0.0
        else:
            detected_language = max(language_scores.items(), key=lambda x: x[1])[0]
            confidence = language_scores[detected_language]
            
            # If confidence is too low, it might be a language we don't recognize
            if confidence < 0.1:
                detected_language = "unknown"
        
        # Format the result
        result = {
            "detected_language": detected_language,
            "language_name": self._get_language_name(detected_language),
            "confidence": round(confidence, 2),
            "all_scores": {lang: round(score, 2) for lang, score in language_scores.items()}
        }
        
        return json.dumps(result)
    
    def _get_language_name(self, language_code):
        """Helper method to get the full language name from a code."""
        language_names = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "unknown": "Unknown"
        }
        return language_names.get(language_code, "Unknown")


if __name__ == "__main__":
    # Test with different languages
    test_messages = [
        "Hello, how are you doing today? I would like some information about your services.",
        "Hola, ¿cómo estás hoy? Me gustaría obtener información sobre sus servicios.",
        "Bonjour, comment allez-vous aujourd'hui? Je voudrais des informations sur vos services.",
        "Hallo, wie geht es Ihnen heute? Ich hätte gerne Informationen über Ihre Dienstleistungen.",
        "Ciao, come stai oggi? Vorrei alcune informazioni sui tuoi servizi."
    ]
    
    for test_message in test_messages:
        tool = DetectLanguage(message=test_message)
        result = tool.run()
        print(f"Message: '{test_message}'")
        print(f"Result: {result}\n") 