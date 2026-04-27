from agent.inference import run_inference


class Agent:
    def __init__(self, skill_registry, domain_classifier=None):
        self.skill_registry = skill_registry
        self.domain_classifier = domain_classifier

    def handle_query(self, query, history=None):
        if history is None:
            history = []

        if self.domain_classifier:
            return self._two_stage_inference(query, history)
        else:
            return self._single_stage_inference(query, history)

    def _two_stage_inference(self, query, history):
        """两阶段推理：先选域，再精确匹配意图"""
        # Stage 1: 域分类
        stage1_prompt = self.domain_classifier.get_stage1_prompt(query)
        domain_output = run_inference(stage1_prompt, history)
        domain_name = self.domain_classifier.match_domain(domain_output)

        if not domain_name:
            return f"无法识别功能域，原始输出: {domain_output}"

        print(f"  [Stage 1] 识别域: {domain_name}")

        # Stage 2: 域内意图精确匹配
        stage2_prompt = self.domain_classifier.get_stage2_prompt(domain_name, query)
        result = run_inference(stage2_prompt, history)

        print(f"  [Stage 2] 匹配结果: {result}")
        return result

    def _single_stage_inference(self, query, history):
        """单阶段推理（兜底）"""
        matched = self.skill_registry.search_skills(query)
        prompt = f"用户query: {query}\n可用技能: {list(matched.keys())}"
        return run_inference(prompt, history)