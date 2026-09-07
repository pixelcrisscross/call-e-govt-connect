from calle import CalleClient
from app.config import settings

client = CalleClient(api_key=settings.CALLE_API_KEY)

INCIDENT_SCHEMA = {
    "type": "object",
    "required": ["city", "location", "issue_type", "severity"],
    "properties": {
        "city": {"type": "string"},
        "location": {"type": "string"},
        "issue_type": {"type": "string"},
        "severity": {"type": "string", "enum": ["low", "medium", "high", "emergency"]}
    }
}

AGENT_GOAL = """
You are 'Call-E', the AI Municipal Dispatcher.
Collect incident reports. 
1. Greet and ask for issue.
2. Ask for CITY and STREET ADDRESS.
3. Run verify_location MCP tool; if invalid, ask for clarification.
4. Collect severity.
5. Thank caller and end.
"""

def configure_agent(webhook_url: str):
    agent = client.agents.create(
        name="Municipal Incident Dispatcher",
        goal=AGENT_GOAL,
        result_schema=INCIDENT_SCHEMA,
        mcp_servers=[{"name": "LocationVerificationServer", "url": settings.MCP_SERVER_URL}],
        webhook_url=webhook_url
    )
    client.numbers.update(
        phone_number=settings.CALLE_PHONE_NUMBER,
        agent_id=agent.id
    )
    print(f"✅ Agent {agent.id} attached to {settings.CALLE_PHONE_NUMBER}")
    return agent