print("Interpreter is working 🚀")

from dotenv import load_dotenv
import os

load_dotenv()
print("API KEY:", os.getenv("OPENAI_API_KEY"))
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform mathematical calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Search for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

from openai import OpenAI
import json
from tools import calculate, search

client = OpenAI()

messages = [
    {
        "role": "system",
        "content": """You are an intelligent agent.
You can reason step-by-step.
Use tools when necessary.
Always think before acting."""
    }
]

def execute_tool(name, arguments):
    if name == "calculate":
        return calculate(arguments["expression"])
    elif name == "search":
        return search(arguments["query"])
    else:
        return "Unknown tool"

def agent_loop(user_input):
    messages.append({"role": "user", "content": user_input})

    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools_schema,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # If tool call requested
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            tool_name = tool_call.function.name
            try:
                arguments = json.loads(tool_call.function.arguments)
            except (json.JSONDecodeError, TypeError):
                arguments = {}

            print(f"\n🧠 Agent decided to call tool: {tool_name}")
            print(f"📥 Arguments: {arguments}")
            result = execute_tool(tool_name, arguments)

            print(f"📤 Tool Result: {result}")

            messages.append(message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        else:
            messages.append(message)
            return message.content

if __name__ == "__main__":
    question = "What is 18% of India's GDP growth?"
    answer = agent_loop(question)
    print("\nFinal Answer:\n", answer)
