"""
Application entry point module.
Provides an interactive CLI session to test conversational and tool-calling execution paths.
"""

import utils.clients
import utils.http_session
import utils.transport
import utils.session
from agent import run_agent

def start_interactive_session():
    print("=" * 60)
    print("Autonomous Safe Agent Console")
    print("Commands: 'exit' or 'quit' to stop | 'role customer' | 'role admin'")
    print("=" * 60)

    current_role = "customer"

    while True:
        try:
            user_input = input(f"\nUser > ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("Session terminated.")
                break

            if user_input.lower().startswith("role "):
                new_role = user_input.split()[1].lower()
                if new_role in ["customer", "admin"]:
                    current_role = new_role
                    print(f"Active role switched to: {current_role}")
                else:
                    print("Invalid role. Available: customer, admin")
                continue

            response = run_agent(prompt=user_input, role=current_role)
            print(f"\n[Agent] > {response}")

        except (KeyboardInterrupt, EOFError):
            print("\nSession aborted.")
            break

if __name__ == "__main__":
    start_interactive_session()