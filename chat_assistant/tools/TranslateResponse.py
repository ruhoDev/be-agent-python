from agency_swarm.tools import BaseTool
from pydantic import Field
import json
from dotenv import load_dotenv

load_dotenv()

class TranslateResponse(BaseTool):
    """
    Translates a response to a different language.
    This tool allows for translating responses to match the user's preferred language.
    """
    
    response: str = Field(
        ..., description="The response text to translate."
    )
    
    target_language: str = Field(
        ..., description="The language code to translate to (e.g., 'es' for Spanish, 'fr' for French)."
    )

    def run(self):
        """
        Translate the response to the target language.
        Returns the translated text or an error if the language is not supported.
        """
        if not self.response.strip():
            return json.dumps({
                "status": "error",
                "message": "Response cannot be empty"
            })
            
        # In a production environment, you would use a proper translation API
        # such as Google Translate, DeepL, or another translation service
        # For this example, we'll implement a simple dictionary-based translation
            
        # Supported languages and their translations for common phrases
        translations = {
            "en": {  # English (source language)
                "Hello! Welcome to our chat service. How can I assist you today?": {
                    "es": "¡Hola! Bienvenido a nuestro servicio de chat. ¿Cómo puedo ayudarte hoy?",
                    "fr": "Bonjour ! Bienvenue sur notre service de chat. Comment puis-je vous aider aujourd'hui ?",
                    "de": "Hallo! Willkommen bei unserem Chat-Service. Wie kann ich Ihnen heute helfen?",
                    "it": "Ciao! Benvenuto al nostro servizio di chat. Come posso aiutarti oggi?"
                },
                "Hello again! How can I help you today?": {
                    "es": "¡Hola de nuevo! ¿Cómo puedo ayudarte hoy?",
                    "fr": "Bonjour à nouveau ! Comment puis-je vous aider aujourd'hui ?",
                    "de": "Hallo nochmal! Wie kann ich Ihnen heute helfen?",
                    "it": "Ciao di nuovo! Come posso aiutarti oggi?"
                },
                "Thank you for chatting with us today. Have a great day!": {
                    "es": "Gracias por chatear con nosotros hoy. ¡Que tengas un buen día!",
                    "fr": "Merci d'avoir discuté avec nous aujourd'hui. Passez une bonne journée !",
                    "de": "Vielen Dank für den Chat mit uns heute. Haben Sie einen schönen Tag!",
                    "it": "Grazie per aver chattato con noi oggi. Buona giornata!"
                },
                "You're welcome! Is there anything else I can help you with?": {
                    "es": "¡De nada! ¿Hay algo más en lo que pueda ayudarte?",
                    "fr": "Je vous en prie ! Y a-t-il autre chose que je puisse faire pour vous ?",
                    "de": "Gern geschehen! Gibt es noch etwas, womit ich Ihnen helfen kann?",
                    "it": "Prego! C'è qualcos'altro in cui posso aiutarti?"
                },
                "I understand. Is there anything specific you'd like to know or discuss?": {
                    "es": "Entiendo. ¿Hay algo específico que te gustaría saber o discutir?",
                    "fr": "Je comprends. Y a-t-il quelque chose de spécifique dont vous aimeriez discuter ?",
                    "de": "Ich verstehe. Gibt es etwas Bestimmtes, das Sie wissen möchten oder besprechen möchten?",
                    "it": "Capisco. C'è qualcosa di specifico che vorresti sapere o discutere?"
                },
                "I'm sorry to hear that. Is there anything I can do to help improve the situation?": {
                    "es": "Lamento escuchar eso. ¿Hay algo que pueda hacer para ayudar a mejorar la situación?",
                    "fr": "Je suis désolé d'entendre cela. Y a-t-il quelque chose que je puisse faire pour améliorer la situation ?",
                    "de": "Es tut mir leid, das zu hören. Gibt es etwas, das ich tun kann, um die Situation zu verbessern?",
                    "it": "Mi dispiace sentirlo. C'è qualcosa che posso fare per migliorare la situazione?"
                }
            }
        }
        
        # Supported language codes
        supported_languages = ["en", "es", "fr", "de", "it"]
        
        # Check if the target language is supported
        if self.target_language not in supported_languages:
            return json.dumps({
                "status": "error",
                "message": f"Unsupported language code: {self.target_language}. Supported languages are: {', '.join(supported_languages)}"
            })
            
        # If the target language is English, no translation needed
        if self.target_language == "en":
            return json.dumps({
                "status": "success",
                "original_text": self.response,
                "translated_text": self.response,
                "source_language": "en",
                "target_language": "en"
            })
            
        # Check if we have a direct translation for this phrase
        for source_text, translations_dict in translations["en"].items():
            if self.response == source_text and self.target_language in translations_dict:
                translated_text = translations_dict[self.target_language]
                return json.dumps({
                    "status": "success",
                    "original_text": self.response,
                    "translated_text": translated_text,
                    "source_language": "en",
                    "target_language": self.target_language
                })
                
        # If no direct translation is available, we would typically call an external API
        # For this example, we'll return a simulated translation message
        return json.dumps({
            "status": "success",
            "original_text": self.response,
            "translated_text": f"[Translation to {self.target_language} would go here: {self.response}]",
            "source_language": "en",
            "target_language": self.target_language,
            "note": "This is a simulated translation. In a production environment, this would use a proper translation API."
        })


if __name__ == "__main__":
    # Test with different phrases and languages
    test_cases = [
        {
            "response": "Hello! Welcome to our chat service. How can I assist you today?",
            "target_language": "es"
        },
        {
            "response": "Thank you for chatting with us today. Have a great day!",
            "target_language": "fr"
        },
        {
            "response": "This is a custom response that doesn't have a predefined translation.",
            "target_language": "de"
        },
        {
            "response": "Hello! Welcome to our chat service. How can I assist you today?",
            "target_language": "jp"  # Unsupported language
        }
    ]
    
    for test_case in test_cases:
        tool = TranslateResponse(**test_case)
        result = tool.run()
        print(f"Original: '{test_case['response']}'")
        print(f"Target Language: {test_case['target_language']}")
        print(f"Result: {result}\n") 