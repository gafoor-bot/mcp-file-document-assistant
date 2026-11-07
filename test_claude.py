
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("ANTHROPIC_API_KEY is missing from .env")

client = Anthropic(api_key=api_key)

response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=200,
    messages=[
        {
            "role": "user",
            "content": "Explain what an MCP server does in two sentences."
        }
    ]
)

print(response.content[0].text)
