# Simple Chat Agency

A collaborative agent system designed to manage, process, and assist with chat interactions using the Agency Swarm framework.

## Overview

This chat agency consists of three specialized agents that work together to process user messages and provide helpful responses:

1. **Chat Manager**: Handles incoming messages, routes them for processing, and delivers responses to users.
2. **Chat Processor**: Analyzes message content, extracts key information, and prepares it for response generation.
3. **Chat Assistant**: Generates contextually appropriate responses based on the processed information.

## Features

- Message sentiment analysis
- Keyword extraction and categorization
- Response generation based on context
- Translation capabilities
- Platform-specific formatting
- Conversational history management
- Suggested replies generation

## Installation

1. Clone the repository:
```
git clone <repository-url>
```

2. Navigate to the chat_agency directory:
```
cd chat_agency
```

3. Install the required dependencies:
```
pip install -r requirements.txt
```

4. Set up your OpenAI API key in the `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

Run the agency demo in your terminal:

```
python agency.py
```

This will start an interactive terminal demo where you can chat with the agency.

## Agent Descriptions

### Chat Manager
- **Role**: Manages user interactions and message flow
- **Tools**:
  - ReceiveMessage: Processes incoming messages
  - SendResponse: Delivers responses to users
  - ManageConversationHistory: Tracks conversation history
  - CheckUserStatus: Monitors user activity

### Chat Processor
- **Role**: Analyzes and processes message content
- **Tools**:
  - AnalyzeSentiment: Determines message tone
  - ExtractKeywords: Identifies key topics
  - CategorizeMessage: Classifies message type
  - DetectLanguage: Identifies message language

### Chat Assistant
- **Role**: Generates helpful responses to users
- **Tools**:
  - GenerateResponse: Creates context-aware responses
  - TranslateResponse: Translates responses to different languages
  - FormatResponseForPlatform: Adapts responses for different platforms
  - GenerateSuggestions: Provides follow-up suggestions

## Communication Flow

1. User message → Chat Manager
2. Chat Manager → Chat Processor (for analysis)
3. Chat Processor → Chat Assistant (with analysis results)
4. Chat Assistant → Chat Manager (with generated response)
5. Chat Manager → User (final response)

## Customization

You can customize this agency by:
- Modifying the tools to add new capabilities
- Adjusting agent instructions to change behavior
- Adding new agents for specialized tasks
- Changing the communication flow in the agency.py file

## License

[MIT License](LICENSE) 