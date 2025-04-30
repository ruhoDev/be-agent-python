from agency_swarm import Agent

class ChatProcessor(Agent):
    def __init__(self):
        super().__init__(
            name="Chat Processor",
            description="Analyzes and processes the content of chat messages to extract meaning, intent, and key information.",
            instructions="./instructions.md",
            tools_folder="./tools",
            temperature=0.3,
            max_prompt_tokens=25000,
        ) 