import unittest
from matcher.match_job import match_score, analyze_match
from analyzer.cv_analyzer import analyze_cv_for_search

class TestMatching(unittest.TestCase):

    def test_adaptive_matching(self):
        """Test the adaptive matching logic with a sample CV and job."""
        cv_text = """
        John Doe - Senior Software Engineer
        ------------------------------------
        A highly experienced software engineer with over 10 years of experience in Python, Django, and React.
        Proven track record of leading teams and delivering high-quality software.
        Interested in fintech and remote opportunities.
        """

        job_text = """
        Senior Python Developer - Fintech Startup
        -----------------------------------------
        We are looking for a senior Python developer to join our growing team.
        Experience with Django and React is a must.
        This is a full-time, remote position in the fintech industry.
        """

        # 1. Analyze the CV to get the profile
        cv_profile = analyze_cv_for_search(cv_text)
        print("Generated CV Profile:", cv_profile)

        # 2. Calculate the match score using the profile
        score = match_score(cv_text, job_text, cv_profile)
        analysis = analyze_match(cv_text, job_text, cv_profile)
        print("Calculated Score:", score)
        print("Match Analysis:", analysis)


        # 3. Assertions
        self.assertGreater(score, 0.5, "The match score should be high for this ideal match.")
        self.assertEqual(analysis['job_level'], 'senior', "The detected job level should be senior.")
        self.assertIn('python', analysis['matching_keywords'], "Python should be a matching keyword.")
        self.assertIn('django', analysis['matching_keywords'], "Django should be a matching keyword.")
        self.assertIn('react', analysis['matching_keywords'], "React should be a matching keyword.")
        self.assertEqual(analysis['match_strength'], 'Strong', "The match strength should be Strong.")

    def test_mismatched_job(self):
        """Test with a clearly mismatched job to ensure a low score."""
        cv_text = """
        Jane Smith - Graphic Designer
        -----------------------------
        Creative graphic designer with expertise in Adobe Creative Suite, Figma, and UI/UX principles.
        Loves creating beautiful and user-friendly designs.
        """

        job_text = """
        Senior Python Developer - Fintech Startup
        -----------------------------------------
        We are looking for a senior Python developer to join our growing team.
        Experience with Django and React is a must.
        This is a full-time, remote position in the fintech industry.
        """

        cv_profile = analyze_cv_for_search(cv_text)
        score = match_score(cv_text, job_text, cv_profile)

        self.assertLess(score, 0.2, "The match score should be low for a mismatched job.")

if __name__ == '__main__':
    unittest.main()
