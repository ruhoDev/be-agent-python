"""
Configuration module for the Simple Chat Agency.
Provides centralized configuration management with environment variable support.
"""
import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

# Load environment variables from .env file
load_dotenv()

@dataclass
class SlackConfig:
    """Slack API configuration"""
    bot_token: Optional[str] = None
    signing_secret: Optional[str] = None
    app_token: Optional[str] = None
    
    @classmethod
    def from_env(cls):
        """Create from environment variables"""
        return cls(
            bot_token=os.environ.get("SLACK_BOT_TOKEN"),
            signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
            app_token=os.environ.get("SLACK_APP_TOKEN")
        )
    
    @property
    def is_configured(self):
        """Check if required slack settings are configured"""
        return self.bot_token is not None and self.signing_secret is not None

@dataclass
class AsyncConfig:
    """Async processing configuration"""
    max_workers: int = 10
    task_timeout: int = 60
    
    @classmethod
    def from_env(cls):
        """Create from environment variables"""
        return cls(
            max_workers=int(os.environ.get("MAX_WORKERS", 10)),
            task_timeout=int(os.environ.get("TASK_TIMEOUT", 60))
        )

@dataclass
class FlaskConfig:
    """Flask web server configuration"""
    debug: bool = False
    port: int = 5000
    host: str = "0.0.0.0"
    
    @classmethod
    def from_env(cls):
        """Create from environment variables"""
        return cls(
            debug=os.environ.get("FLASK_DEBUG", "False").lower() == "true",
            port=int(os.environ.get("PORT", 5000)),
            host=os.environ.get("HOST", "0.0.0.0")
        )

@dataclass
class OpenAIConfig:
    """OpenAI API configuration"""
    api_key: Optional[str] = None
    model: str = "gpt-4o"
    temperature: float = 0.4
    max_tokens: int = 1000
    
    @classmethod
    def from_env(cls):
        """Create from environment variables"""
        return cls(
            api_key=os.environ.get("OPENAI_API_KEY"),
            model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
            temperature=float(os.environ.get("OPENAI_TEMPERATURE", 0.4)),
            max_tokens=int(os.environ.get("OPENAI_MAX_TOKENS", 1000))
        )
    
    @property
    def is_configured(self):
        """Check if OpenAI is configured"""
        return self.api_key is not None

@dataclass
class AppConfig:
    """Main application configuration"""
    slack: SlackConfig
    async_config: AsyncConfig
    flask: FlaskConfig
    openai: OpenAIConfig
    
    @classmethod
    def from_env(cls):
        """Create from environment variables"""
        return cls(
            slack=SlackConfig.from_env(),
            async_config=AsyncConfig.from_env(),
            flask=FlaskConfig.from_env(),
            openai=OpenAIConfig.from_env()
        )
    
    def validate(self):
        """
        Validate required configuration values
        
        Raises:
            ValueError: If required configuration is missing
        """
        missing = []
        
        if not self.openai.is_configured:
            missing.append("OPENAI_API_KEY")
            
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True

# Global config instance
config = AppConfig.from_env()
