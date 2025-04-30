from agency_swarm.tools import BaseTool
from pydantic import Field
import json
import re
from dotenv import load_dotenv

load_dotenv()

class FormatResponseForPlatform(BaseTool):
    """
    Formats a response for a specific platform or channel.
    This tool adapts responses to suit different communication platforms
    by applying platform-specific formatting and constraints.
    """
    
    response: str = Field(
        ..., description="The response text to format."
    )
    
    platform: str = Field(
        ..., description="The platform to format for (e.g., 'sms', 'email', 'web', 'mobile')."
    )

    def run(self):
        """
        Format the response according to the specified platform's requirements.
        Returns the formatted response or an error if the platform is not supported.
        """
        if not self.response.strip():
            return json.dumps({
                "status": "error",
                "message": "Response cannot be empty"
            })
            
        # Supported platforms and their formatting requirements
        supported_platforms = ["sms", "email", "web", "mobile", "slack", "whatsapp", "twitter"]
        
        # Check if the platform is supported
        if self.platform.lower() not in supported_platforms:
            return json.dumps({
                "status": "error",
                "message": f"Unsupported platform: {self.platform}. Supported platforms are: {', '.join(supported_platforms)}"
            })
            
        # Format the response based on the platform
        formatted_response = self._format_for_platform(self.response, self.platform.lower())
        
        return json.dumps({
            "status": "success",
            "original_response": self.response,
            "formatted_response": formatted_response,
            "platform": self.platform.lower()
        })
    
    def _format_for_platform(self, response, platform):
        """Format the response according to the platform's requirements."""
        if platform == "sms":
            # SMS: Keep it short (160 chars max), no rich formatting
            formatted = self._format_for_sms(response)
        elif platform == "email":
            # Email: Can include HTML formatting, longer responses
            formatted = self._format_for_email(response)
        elif platform == "web":
            # Web: Can include HTML and CSS styling
            formatted = self._format_for_web(response)
        elif platform == "mobile":
            # Mobile: Shorter than web but longer than SMS, limited formatting
            formatted = self._format_for_mobile(response)
        elif platform == "slack":
            # Slack: Can use Slack-specific markdown formatting
            formatted = self._format_for_slack(response)
        elif platform == "whatsapp":
            # WhatsApp: Similar to SMS but with support for some formatting
            formatted = self._format_for_whatsapp(response)
        elif platform == "twitter":
            # Twitter: Very strict character limit (280 chars)
            formatted = self._format_for_twitter(response)
        else:
            # Default - minimal formatting
            formatted = response
            
        return formatted
    
    def _format_for_sms(self, response):
        """Format for SMS: Character limit, no rich formatting."""
        # Truncate to 160 characters if needed
        if len(response) > 160:
            truncated = response[:157] + "..."
            return truncated
        return response
    
    def _format_for_email(self, response):
        """Format for email: Can include HTML formatting."""
        # Add basic HTML formatting
        formatted = f"<p>{response}</p>"
        
        # Replace URLs with HTML links
        url_pattern = r'https?://[^\s]+'
        formatted = re.sub(url_pattern, lambda m: f'<a href="{m.group(0)}">{m.group(0)}</a>', formatted)
        
        # Add email signature
        formatted += "<p>---<br>Chat Support Team</p>"
        
        return formatted
    
    def _format_for_web(self, response):
        """Format for web: Can include HTML and CSS styling."""
        # Add more extensive HTML formatting
        formatted = f'<div class="chat-response">{response}</div>'
        
        # Replace URLs with HTML links
        url_pattern = r'https?://[^\s]+'
        formatted = re.sub(url_pattern, lambda m: f'<a href="{m.group(0)}" class="chat-link">{m.group(0)}</a>', formatted)
        
        # Replace emojis with span elements for better styling
        emoji_pattern = r':([\w_]+):'  # Simple pattern for emoji codes like :smile:
        formatted = re.sub(emoji_pattern, lambda m: f'<span class="emoji emoji-{m.group(1)}"></span>', formatted)
        
        return formatted
    
    def _format_for_mobile(self, response):
        """Format for mobile: Shorter than web, limited formatting."""
        # Truncate if very long (500 chars max)
        if len(response) > 500:
            truncated = response[:497] + "..."
            return truncated
        return response
    
    def _format_for_slack(self, response):
        """Format for Slack: Use Slack-specific markdown."""
        # Convert basic formatting to Slack markdown
        formatted = response
        
        # Bold: *text* -> *text*
        # Italic: _text_ -> _text_
        # Code: `code` -> `code`
        # Code blocks: ```code``` -> ```code```
        
        # Add Slack-specific formatting for lists
        list_pattern = r'^\s*[-*]\s+(.*?)$'
        formatted = re.sub(list_pattern, r'• \1', formatted, flags=re.MULTILINE)
        
        return formatted
    
    def _format_for_whatsapp(self, response):
        """Format for WhatsApp: Similar to SMS but with some formatting."""
        # WhatsApp supports some basic formatting like *bold* and _italic_
        formatted = response
        
        # Ensure it's not too long (WhatsApp has a limit but it's quite large)
        if len(formatted) > 1000:
            formatted = formatted[:997] + "..."
            
        return formatted
    
    def _format_for_twitter(self, response):
        """Format for Twitter: Very strict character limit."""
        # Twitter has a 280 character limit
        if len(response) > 280:
            truncated = response[:277] + "..."
            return truncated
        return response


if __name__ == "__main__":
    # Test with different platforms and a sample response
    test_response = "Hello! Thank you for your message. We're happy to help with your inquiry about our services. Please let us know if you have any other questions or if you need additional information about our products. You can also visit our website at https://example.com for more details."
    
    platforms = ["sms", "email", "web", "mobile", "slack", "whatsapp", "twitter", "unsupported_platform"]
    
    for platform in platforms:
        tool = FormatResponseForPlatform(response=test_response, platform=platform)
        result = tool.run()
        print(f"Platform: {platform}")
        print(f"Result: {result}\n") 