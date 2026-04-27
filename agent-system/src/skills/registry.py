class SkillRegistry:
    def __init__(self):
        self.skills = {}
        self.domains = {}

    def register_skill(self, skill_name, skill_description, api_definition=None):
        self.skills[skill_name] = {
            "description": skill_description,
            "api": api_definition
        }

    def register_domain(self, domain_name, domain_description, skills):
        """注册一个域及其下所有技能"""
        self.domains[domain_name] = {
            "description": domain_description,
            "skills": [s["name"] for s in skills]
        }
        for skill in skills:
            self.register_skill(skill["name"], skill["description"])

    def get_skill(self, skill_name):
        return self.skills.get(skill_name)

    def get_domain(self, domain_name):
        return self.domains.get(domain_name)

    def search_skills(self, query):
        matching_skills = {}
        for skill_name, skill_info in self.skills.items():
            if query.lower() in skill_name.lower() or query.lower() in skill_info["description"].lower():
                matching_skills[skill_name] = skill_info
        return matching_skills

    def list_skills(self):
        return list(self.skills.keys())

    def list_domains(self):
        return list(self.domains.keys())