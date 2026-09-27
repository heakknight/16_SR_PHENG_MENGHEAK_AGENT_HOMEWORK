"""
Autonomous agent control loop module.
Orchestrates prompt dispatch, tool invocation, observation ingest, and response termination.
"""

import json
import ollama
from config import LLM_MODEL, MAX_ITERATIONS, SYSTEM_PROMPT
from harness import execute_safe_tool
from tools import (
    search_products,
    check_stock,
    buy_product,
    delete_product,
    restock_product,
)

TOOL_REGISTRY_FUNCTIONS = [
    search_products,
    check_stock,
    buy_product,
    delete_product,
    restock_product,
]


def run_agent(prompt: str, role: str = "customer") -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    for step in range(1, MAX_ITERATIONS + 1):
        try:
            response = ollama.chat(
                model=LLM_MODEL,
                messages=messages,
                tools=TOOL_REGISTRY_FUNCTIONS,
            )
        except Exception as err:
            return f"Error connecting to Ollama: {err}"

        assistant_message = response.get("message", {})
        messages.append(assistant_message)

        tool_calls = assistant_message.get("tool_calls")

        if not tool_calls:
            return assistant_message.get("content", "").strip()

        for call in tool_calls:
            tool_name = call.get("function", {}).get("name")
            tool_args = call.get("function", {}).get("arguments", {})

            print(f"[action] calling {tool_name} with {tool_args}")

            observation = execute_safe_tool(
                role=role,
                tool_name=tool_name,
                raw_args=tool_args,
            )

            print(f"[observation] {observation}")

            messages.append({
                "role": "tool",
                "content": json.dumps(observation),
            })

    return f"Stopped: reached max iterations limit ({MAX_ITERATIONS})."