class DomainClassifier:
    """两阶段推理：先选大类域，再注入该域详细意图做精确匹配"""

    def __init__(self, domains):
        """
        Args:
            domains: list of domain dicts from skills.json["domains"]
        """
        self.domains = {d["name"]: d for d in domains}

    def get_stage1_prompt(self, user_query):
        """第一阶段：只给域名+简要描述，让模型选域"""
        lines = [
            "你是车机语音语义理解助手。请根据用户指令判断属于以下哪个功能域，只输出域名。",
            ""
        ]
        for name, info in self.domains.items():
            lines.append(f"- 【{name}】：{info['description']}")
        lines.append("")
        lines.append(f"用户指令：{user_query}")
        lines.append("请只输出一个域名，不要解释。")
        return "\n".join(lines)

    def get_stage2_prompt(self, domain_name, user_query):
        """第二阶段：注入选中域的全部意图详情，精确匹配"""
        domain = self.domains.get(domain_name)
        if not domain:
            return None
        lines = [
            f"用户指令属于【{domain_name}】，以下是该域所有可用意图：",
            ""
        ]
        for skill in domain["skills"]:
            lines.append(f"- {skill['name']}：{skill['description']}")
        lines.append("")
        lines.append(f"用户指令：{user_query}")
        lines.append("请从以上意图中选择最匹配的一个，输出格式：ASR结果|意图名称")
        return "\n".join(lines)

    def match_domain(self, model_output):
        """从模型输出中匹配域名"""
        for name in self.domains:
            if name in model_output:
                return name
        return None

    def list_domains(self):
        return list(self.domains.keys())

    def get_domain_skills(self, domain_name):
        domain = self.domains.get(domain_name)
        return domain["skills"] if domain else []