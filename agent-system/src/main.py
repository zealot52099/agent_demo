import json
import sys
import io

sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

from agent.agent import Agent
from skills.registry import SkillRegistry
from skills.domain_classifier import DomainClassifier

def load_skills():
    with open('configs/skills.json', 'r') as f:
        return json.load(f)

def main():
    config = load_skills()
    skill_registry = SkillRegistry()

    # 按域注册所有技能
    for domain in config["domains"]:
        skill_registry.register_domain(
            domain["name"],
            domain["description"],
            domain["skills"]
        )

    # 初始化域分类器（两阶段推理）
    domain_classifier = DomainClassifier(config["domains"])

    agent = Agent(skill_registry, domain_classifier)
    history = []

    print("Welcome to the Agent System! How can I assist you today?")

    while True:
        query = input("You: ")
        if query.lower() in ['exit', 'quit']:
            print("Exiting the Agent System. Goodbye!")
            break

        response = agent.handle_query(query, history)
        history.append({"query": query, "response": response})
        print(f"Agent: {response}")

if __name__ == "__main__":
    main()