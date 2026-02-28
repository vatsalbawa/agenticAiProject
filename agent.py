print("Interpreter is working 🚀")

from ast import arguments
import re

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
    "content": """
You are an execution agent.

Rules:
- Use tool outputs carefully.
- If tool returns JSON, extract numeric values.
- Never invent variables like GDP.
- Always use concrete numeric expressions.
"""
}
]

def is_valid_expression(expr):
    return re.match(r'^[0-9\.\*\+\-\/\s]+$', expr)

def execute_tool(name, arguments):
    # if name == "calculate":
    #     return calculate(arguments["expression"])
    # elif name == "search":
    #     return search(arguments["query"])
    # else:
    #     return "Unknown tool"
    if name == "calculate":
        return calculate(arguments["expression"])
    elif name == "search":
        return search(arguments["query"])
    else:
        return {"error": "Unknown tool"}

def agent_loop(user_input):
    messages.append({"role": "user", "content": user_input})

    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools_schema,
            tool_choice="auto"
            # tool_choice={
            #     "type": "function",
            #     "function": {"name": "search"}
            # }
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

def create_plan(user_input):
    planner_prompt = f"""
You are a strict planning agent.

ORIGINAL USER TASK:
\"\"\"{user_input}\"\"\"

Rules:
- You MUST preserve the exact meaning of the original task.
- Do NOT change terminology.
- If the task says "GDP growth", you must use "GDP growth".
- Do NOT replace it with "GDP".
- Do NOT broaden or reinterpret the objective.
- Create only minimal executable steps required to complete this exact task.

Return only numbered steps.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": planner_prompt}],
        temperature=0
    )

    return response.choices[0].message.content

def parse_plan(plan_text):
    steps = []
    for line in plan_text.split("\n"):
        if line.strip() and line[0].isdigit():
            steps.append(line.split(".", 1)[1].strip())
    return steps

def execute_plan(user_input):
    plan_text = create_plan(user_input)
    print("\n🧠 PLAN:\n", plan_text)

    steps = parse_plan(plan_text)

    state = {}
    context_messages = [
        {
            "role": "system",
            "content": "You must ONLY use numeric values explicitly returned by tools. Do not invent, approximate, or modify numeric values. If tool says 7, use 7."
        }
    ]

    for step in steps:
        print(f"\n🔹 Executing Step: {step}")

        context_messages.append({
            "role": "user",
            "content": step
        })

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=context_messages,
            tools=tools_schema,
            tool_choice="auto",
            temperature=0
        )

        message = response.choices[0].message

        # if message.tool_calls:
        #     tool_call = message.tool_calls[0]
        #     tool_name = tool_call.function.name
        #     arguments = json.loads(tool_call.function.arguments)

        #     print(f"🛠 Tool Call: {tool_name} {arguments}")

        #     result = execute_tool(tool_name, arguments)
        #     print(f"📤 Tool Result: {result}")

        #     context_messages.append(message)
        #     context_messages.append({
        #         "role": "tool",
        #         "tool_call_id": tool_call.id,
        #         "content": result
        #     })
        # 
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f"\n🛠 Tool Call: {tool_name} {arguments}")

            result = execute_tool(tool_name, arguments)
            print(f"📤 Tool Result: {result}")

            # 🔥 STATE STORAGE
            if tool_name == "search":
                try:
                    data = json.loads(result)
                    if "gdp_growth" in data:
                        state["gdp_growth"] = data["gdp_growth"]
                        print("📦 Stored in state: gdp_growth =", state["gdp_growth"])
                        # ✅ STEP 4 GOES HERE
                        growth = state["gdp_growth"]
                        expression = f"{growth} * 0.18"
                        calc_result = calculate(expression)

                        state["result"] = calc_result

                        final_answer = f"18% of India's GDP growth ({growth}%) is {calc_result}%."
                        return final_answer
                except:
                    pass

            context_messages.append({
                "role": "assistant",
                "content": result
            })
        else:
            context_messages.append(message)
            print(f"📝 Step Result: {message.content}")
    
    last_message = context_messages[-1]

    if hasattr(last_message, "content"):
        return last_message.content
    else:
        return last_message.get("content", "")

if __name__ == "__main__":
    question = "What is 18% of India's GDP growth?"
    answer = execute_plan(question)
    print("\n✅ Final Answer:\n", answer)
    #question = "What is 18% of India's GDP growth?"
    #answer = agent_loop(question)
    #print("\nFinal Answer:\n", answer)
