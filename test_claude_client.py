
from claude_client import generate_answer

question = "How many paid vacation days do employees receive?"

context = """
Employees receive 15 days of paid time off annually.
"""

answer = generate_answer(question, context)

print("\nClaude's Answer:")
print(answer)
