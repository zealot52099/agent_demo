"""交互式入口（保留命令行模式）。"""
import os
import json
import sys
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

from agent.agent import Agent
from skills.registry import SkillRegistry
from skills.domain_classifier import DomainClassifier
from agent_system.config import settings
from agent_system.logging_config import logger


def load_skills():
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "configs", "skills.json"
    )
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    logger.info("Starting Agent System...")

    config = load_skills()
    skill_registry = SkillRegistry()

    for domain in config["domains"]:
        skill_registry.register_domain(
            domain["name"],
            domain["description"],
            domain["skills"]
        )

    domain_classifier = DomainClassifier(config["domains"])
    agent = Agent(
        skill_registry=skill_registry,
        domain_classifier=domain_classifier,
        session_id="cli_session",
        enable_planning=True,
        enable_execution=False
    )

    logger.info("Agent initialized successfully")
    print("Welcome to the Agent System! How can I assist you today?")
    print(f"Mock mode: {settings.mock_mode}")
    print("Type 'exit' or 'quit' to exit, 'history' to view history\n")

    while True:
        try:
            query = input("You: ")
            if query.lower() in ['exit', 'quit']:
                print("Exiting the Agent System. Goodbye!")
                break

            if query.lower() == 'history':
                history = agent.get_history()
                print("\n--- History ---")
                for msg in history:
                    print(f"  [{msg['role']}]: {msg['content'][:50]}...")
                print()
                continue

            response = agent.handle_query(
                query,
                enable_execute=True,
                return_full_result=False
            )
            print(f"Agent: {response}\n")

        except EOFError:
            print("\nExiting (EOF)...")
            break
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()