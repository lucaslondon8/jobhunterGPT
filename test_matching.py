import unittest
from analyzer.ai_analyzer import AIJobAnalyzer

class TestAIMatching(unittest.TestCase):

    def setUp(self):
        self.analyzer = AIJobAnalyzer()
        self.cv_text = """
        John Doe - Senior Software Engineer
        ------------------------------------
        A highly experienced software engineer with over 10 years of experience in Python, Django, and React.
        Proven track record of leading teams and delivering high-quality software.
        Interested in fintech and remote opportunities.
        """
        self.job_text = """
        Senior Python Developer - Fintech Startup
        -----------------------------------------
        We are looking for a senior Python developer to join our growing team.
        Experience with Django and React is a must.
        This is a full-time, remote position in the fintech industry.
        """

    def test_ai_cv_analysis(self):
        """Test the AI-powered CV analysis."""
        if not self.analyzer.co:
            self.skipTest("COHERE_API_KEY not found, skipping AI test.")

        cv_profile = self.analyzer.analyze_cv(self.cv_text)

        self.assertIn('summary', cv_profile)
        self.assertIn('technical_skills', cv_profile)
        self.assertIn('specific_roles', cv_profile)
        self.assertIn('experience_level', cv_profile)
        self.assertIn('target_industries', cv_profile)
        self.assertIn('python', [skill.lower() for skill in cv_profile['technical_skills']])

    def test_ai_job_matching(self):
        """Test the AI-powered job matching."""
        if not self.analyzer.co:
            self.skipTest("COHERE_API_KEY not found, skipping AI test.")

        cv_profile = self.analyzer.analyze_cv(self.cv_text)
        match_result = self.analyzer.match_job(cv_profile, self.job_text)

        self.assertIn('score', match_result)
        self.assertIn('rationale', match_result)
        self.assertGreater(match_result['score'], 0.5, "The AI match score should be high for this ideal match.")

if __name__ == '__main__':
    unittest.main()
