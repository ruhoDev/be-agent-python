from agency_swarm import Agent, Agency
from shared_roles import AGENT_ROLES

def create_agent(name: str, role_key: str, model="gpt-4o") -> Agent:
    return Agent(
        name=name,
        instructions=AGENT_ROLES[role_key],
        description=f"{role_key} responsible for handling tasks related to {role_key.lower()}",
        model=model
    )

# Sub-agents
quality_agent = create_agent("Quality Agent - Test 1", "Quality Agent")
content_manager = create_agent("Content Manager - Test 1", "Content Manager", model="gpt-4o-mini")
scheduler = create_agent("Scheduler - Test 1", "Scheduler")
data_agent = create_agent("Data Agent - Test 1", "Data Agent")
research_agent = create_agent("Research Agent - Test 1", "Research Agent")
seo_agent = create_agent("SEO Agent - Test 1", "SEO Agent")

# CEO Agent
CEO_PROMPT = """
You are the CEO of this AI agency. Review incoming tasks and assign them to the correct team member based on their role.
You can choose from the following team members:

- Quality Agent: quality control and reviewing
- Content Manager: content creation and editing
- Scheduler: scheduling and calendar tasks
- Data Agent: data analysis and reporting
- Research Agent: deep research and summarization
- SEO Agent: search engine optimization tasks

Ask clarifying questions if needed, and always confirm the task is assigned appropriately.
"""

ceo_agent = Agent(
    name="CEO Agent",
    instructions=CEO_PROMPT,
    description="Oversees all operations and delegates to agents.",
    model="gpt-4o"
)

# Assemble the swarm
agency = Agency([
        ceo_agent,
        [ceo_agent, quality_agent],
        [ceo_agent, content_manager],
        [ceo_agent, scheduler],
        [ceo_agent, data_agent],
        [ceo_agent, research_agent],
        [ceo_agent, seo_agent],
    ],
    shared_instructions="""
# Agency Manifesto

This agency is a collaborative AI swarm designed to handle various specialized tasks through dedicated agents.

## Mission
To provide comprehensive, high-quality assistance across multiple domains by leveraging specialized agent capabilities.

## Context
Each agent has a specific role and expertise. The CEO coordinates and delegates tasks to the appropriate specialist.
""",
    temperature=0.4,
    max_prompt_tokens=25000
)

if __name__ == "__main__":
    agency.demo_gradio()
    agency.run_demo()  # Run the agency in terminal demo mode

