import unittest
from src.skills.skill_search import search_skills

class TestSkillSearch(unittest.TestCase):

    def setUp(self):
        # Setup any necessary data or state before each test
        self.test_queries = [
            "How do I send an email?",
            "What is the weather like today?",
            "How can I reset my password?"
        ]

    def test_search_skills(self):
        for query in self.test_queries:
            with self.subTest(query=query):
                skills = search_skills(query)
                self.assertIsInstance(skills, list)
                self.assertGreater(len(skills), 0, "Expected at least one skill to be returned")

    def test_search_skills_empty_query(self):
        skills = search_skills("")
        self.assertEqual(skills, [], "Expected no skills to be returned for an empty query")

    def test_search_skills_no_match(self):
        skills = search_skills("This query should not match any skills")
        self.assertEqual(skills, [], "Expected no skills to be returned for a non-matching query")

if __name__ == '__main__':
    unittest.main()