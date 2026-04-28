
from agent_system.logging_config import logger

class DomainClassifier:
    """单阶段推理：模型自主决策是否需要域知识，需要时注入该域详细意图做精确匹配"""

    def __init__(self, domains):
        """
        Args:
            domains: list of domain dicts from skills.json["domains"]
        """
        self.domains = {d["name"]: d for d in domains}

    # def get_stage1_prompt(self, user_query):
    #     """第一阶段：只给域名+简要描述，让模型选域"""
    #     # lines = [
    #     #     "你是车机语音语义理解助手。请根据用户指令判断属于以下哪个功能域，只输出域名。",
    #     #     ""
    #     # ]
    #     lines = [
    #         "你是车机语音语义理解助手。请根据用户指令判断属于以下哪个功能域。请你一步步思考后，输出思考过程，再按<domain>域名</domain>的格式输出。",
    #         ""
    #     ]
    #     for name, info in self.domains.items():
    #         lines.append(f"- 【{name}】：{info['description']}")
    #     lines.append("必须注意：如果指令为‘第XX个’、‘第XX条’等表述，需要结合上文对话内容进行判断，不能随意当做噪声动作域。")
    #     lines.append("")
    #     lines.append(f"用户指令：{user_query}")
    #     # lines.append("请只输出一个域名，不要解释。")
        
    #     return "\n".join(lines)

    
    def get_stage1_prompt(self, user_query, history):
        """第一阶段：只给域名+简要描述，让模型选域"""
        # lines = [
        #     "你是车机语音语义理解助手。请根据用户指令判断属于以下哪个功能域，只输出域名。",
        #     ""
        # ]
        lines = [
            "你是车机语音语义理解助手。请根据用户指令判断属于以下哪个功能域。",
            ""
        ]
        for name, info in self.domains.items():
            lines.append(f"- 【{name}】：{info['description']}")
        lines.append("必须注意：1、如果指令为“退下”退下”“再见”等类似指令，说明用户希望车机关闭当前任务，属于‘车辆控制综合域’中的ControlClose；2、如果指令为‘第XX个’、‘第XX条’等表述，需要结合上文对话内容进行判断，不能随意当做噪声动作域。请你一步步思考后，输出思考过程，再按<domain>域名</domain>的格式输出。")
        lines.append("")
        if history:
            lines.append(f"历史对话：{history}")
        lines.append(f"用户指令：{user_query}")
        # lines.append("请只输出一个域名，不要解释。")
        
        return "\n".join(lines)

    # def get_stage2_prompt(self, domain_name, user_query):
    #     """第二阶段：注入选中域的全部意图详情，精确匹配"""
        
    #     domain = self.domains.get(domain_name)
    #     if not domain:
    #         return None
    #     lines = [
    #         f"用户指令属于【{domain_name}】，以下是该域所有可用意图：",
    #         ""
    #     ]
    #     logger.info(f"Domain '{domain_name}' skills for stage 2 prompt:")
    #     for skill in domain["skills"]:
    #         lines.append(f"- {skill['name']}：{skill['description']}")
    #         logger.info(f"  - {skill['name']}: {skill['description']}")
    #     lines.append("")
    #     lines.append(f"用户指令：{user_query}")
    #     # lines.append("请从以上意图中选择最匹配的一个，输出格式：ASR结果|意图名称")

    #     lines.append("请从以上意图中选择最匹配的一个，请一步步思考并输出思考过程，最终输出格式：<think>思考过程</think><answer>ASR结果|意图名称</answer>")
    #     return "\n".join(lines)

    def get_stage2_prompt(self, domain_name, user_query, history):
        """第二阶段：注入选中域的全部意图详情，精确匹配"""
        
        domain = self.domains.get(domain_name)
        if not domain:
            return None
        lines = [
            f"用户指令属于【{domain_name}】，以下是该域所有可用意图：",
            ""
        ]
        logger.info(f"Domain '{domain_name}' skills for stage 2 prompt:")
        for skill in domain["skills"]:
            lines.append(f"- {skill['name']}：{skill['description']}")
            logger.info(f"  - {skill['name']}: {skill['description']}")
        # lines.append("")
        # lines.append("请从以上意图中选择最匹配的一个，请一步步思考并输出思考过程，最终输出格式：<think>思考过程</think><answer>ASR结果|意图名称</answer>")
        lines.append("请从以上意图中选择最匹配的一个，请一步步思考并输出思考过程，最终输出格式：<think>思考过程</think><answer>意图名称</answer>")
        if history:
            lines.append(f"历史对话：{history}")
        lines.append(f"用户指令：{user_query}")
        # lines.append("请从以上意图中选择最匹配的一个，输出格式：ASR结果|意图名称")

        
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

    def get_single_stage_prompt(self, user_query, history):
        """单阶段推理：模型自主决策是否需要域知识"""
        lines = [
            "你是车机语音语义理解助手。请根据用户指令判断其意图。",
            ""
        ]
        lines.append("你可用的功能域如下：")
        for name, info in self.domains.items():
            lines.append(f"- 【{name}】：{info['description']}")
        lines.append("")
        lines.append("重要说明：")
        lines.append("1、如果指令为'退下''再见'等类似指令，说明用户希望车机关闭当前任务，属于'车辆控制综合域'中的ControlClose")
        lines.append("2、如果指令为'第XX个''第XX条'等表述，需要结合上文对话内容进行判断，不能随意当做噪声动作域")
        lines.append("3、如果用户指令可以直接从上述功能域中匹配到明确意图，则直接输出意图；")
        lines.append("  如果需要更详细信息才能准确判断，请先输出<need_domain>域名</need_domain>表明需要该域的详细意图列表")
        lines.append("")
        if history:
            lines.append(f"历史对话：{history}")
        lines.append(f"用户指令：{user_query}")
        lines.append("")
        lines.append("请一步步思考后，输出思考过程，最终按以下格式之一输出：")
        lines.append("  直接输出意图：<answer>意图名称</answer>")
        lines.append("  需要域知识：<need_domain>域名</need_domain>")

        return "\n".join(lines)

    def match_need_domain(self, model_output):
        """从模型输出中匹配是否需要域知识"""
        import re
        match = re.search(r'<need_domain>(.*?)</need_domain>', model_output)
        if match:
            domain_name = match.group(1).strip()
            for name in self.domains:
                if name in domain_name or domain_name in name:
                    return name
        return None

    def match_single_intent(self, model_output):
        """从模型输出中直接提取意图"""
        import re
        match = re.search(r'<answer>(.*?)</answer>', model_output)
        if match:
            return match.group(1).strip()
        return None

    def match_intent_from_domain(self, model_output, domain_name):
        """从域上下文中提取意图"""
        import re
        match = re.search(r'<answer>(.*?)</answer>', model_output)
        if match:
            return match.group(1).strip()
        return None