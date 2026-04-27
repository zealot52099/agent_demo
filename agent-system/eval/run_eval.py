"""离线评测：在 dataset.jsonl 上跑 agent，计算 domain/intent 准确率。"""
import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from skills.registry import SkillRegistry
from skills.domain_classifier import DomainClassifier
from agent.agent import Agent


def load_skills(path="configs/skills.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(dataset="eval/dataset.jsonl"):
    cfg = load_skills()
    reg = SkillRegistry()
    for d in cfg["domains"]:
        reg.register_domain(d["name"], d["description"], d["skills"])
    agent = Agent(reg, DomainClassifier(cfg["domains"]))

    total = 0
    domain_hit = 0
    intent_hit = 0
    confusion = Counter()

    with open(dataset, encoding="utf-8") as f:
        for line in f:
            sample = json.loads(line)
            query = sample["query"]
            gt_domain = sample.get("domain")
            gt_intent = sample["intent"]

            result = agent.handle_query(query, history=[])
            total += 1
            if result.get("domain") == gt_domain:
                domain_hit += 1
            if result.get("intent") == gt_intent:
                intent_hit += 1
            else:
                confusion[(gt_intent, result.get("intent"))] += 1

    print(f"Total: {total}")
    print(f"Domain Acc: {domain_hit / total:.3f}")
    print(f"Intent Acc: {intent_hit / total:.3f}")
    print("Top confusions:")
    for (gt, pred), cnt in confusion.most_common(10):
        print(f"  {gt} -> {pred}: {cnt}")


if __name__ == "__main__":
    main()
