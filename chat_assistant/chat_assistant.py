from agency_swarm import Agent

class ChatAssistant(Agent):
    def __init__(self):
        super().__init__(
            name="Chat Assistant",
            description="Generates helpful, contextually appropriate responses to user messages based on processed information.",
            instructions="./instructions.md",
            tools_folder="./tools",
            temperature=0.5,  # Slightly higher temperature for more varied responses
            max_prompt_tokens=25000,
        ) 