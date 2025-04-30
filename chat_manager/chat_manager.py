from agency_swarm import Agent

class ChatManager(Agent):
    def __init__(self):
        super().__init__(
            name="Chat Manager",
            description="Responsible for handling incoming chat messages, routing them for processing, and delivering responses to users.",
            instructions="./instructions.md",
            tools_folder="./tools",
            temperature=0.3,
            max_prompt_tokens=25000,
        ) 