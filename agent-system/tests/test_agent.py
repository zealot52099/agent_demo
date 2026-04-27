import unittest
from src.agent.agent import Agent
from src.skills.registry import SkillRegistry

class TestAgent(unittest.TestCase):

    def setUp(self):
        self.agent = Agent()
        self.skill_registry = SkillRegistry()

    def test_agent_initialization(self):
        self.assertIsNotNone(self.agent)
        self.assertIsNotNone(self.skill_registry)

    def test_process_query(self):
        query = "What can you do?"
        expected_response = "I can help you with various tasks."
        self.skill_registry.register_skill("help", expected_response)
        response = self.agent.process_query(query)
        self.assertIn(expected_response, response)

    def test_inference_with_audio(self):
        query = "Analyze this audio."
        audio_file = "file://path/to/audio.wav"
        expected_response = "Audio analysis complete."
        self.skill_registry.register_skill("audio_analysis", expected_response)
        response = self.agent.run_inference(query, audio_file)
        self.assertEqual(response, expected_response)

    def test_skill_search(self):
        query = "Show me skills related to analysis."
        self.skill_registry.register_skill("data_analysis", "Analyze data.")
        skills = self.skill_registry.search_skills(query)
        self.assertIn("data_analysis", skills)

if __name__ == '__main__':
    unittest.main()