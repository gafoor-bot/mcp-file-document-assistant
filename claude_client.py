
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("ANTHROPIC_API_KEY is missing from .env")

client = Anthropic(api_key=api_key)


def generate_answer(question: str, context: str) -> str:
    """Generate an answer using Claude and retrieved document context."""

    response = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=500,
        system=(
            "You are a document assistant. Answer questions using only "
            "the supplied document context. If the answer is not present "
            "in the context, clearly say you could not find the answer. "
            "Do not invent facts."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Document context:\n{context}\n\n"
                    "Provide a clear, concise answer."
                )
            }
        ]
    )

    return "\n".join(
        block.text
        for block in response.content
        if block.type == "text"
    )
