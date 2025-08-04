# analyzer/ai_analyzer.py

import os
from cohere import Client
from dotenv import load_dotenv

load_dotenv()

class AIJobAnalyzer:
    """
    A class to analyze CVs and job descriptions using AI.
    """
    def __init__(self):
        self.cohere_api_key = os.getenv("COHERE_API_KEY")
        if not self.cohere_api_key:
            print("⚠️  COHERE_API_KEY not found - AI analysis will be disabled.")
            self.co = None
        else:
            self.co = Client(self.cohere_api_key)

    def analyze_cv(self, cv_text: str) -> dict:
        """
        Analyzes a CV using the Cohere API to extract key information.
        """
        if not self.co:
            return {}

        prompt = f"""Analyze the following CV and extract the information in a JSON format.
        The JSON should have the following keys: "summary", "technical_skills", "specific_roles", "experience_level", "target_industries".

        CV:
        ---
        {cv_text}
        ---

        JSON Output:
        """

        try:
            response = self.co.chat(
                model="command-r",
                message=prompt,
                temperature=0.2,
            )
            # Extract the JSON part from the response
            json_text = response.text.strip()
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0]

            import json
            return json.loads(json_text)
        except Exception as e:
            print(f"Error analyzing CV with AI: {e}")
            return {}

    def match_job(self, cv_profile: dict, job_text: str) -> dict:
        """
        Matches a CV profile to a job description using the Cohere API.
        """
        if not self.co:
            return {}

        prompt = f"""
        Based on the following CV profile and job description, calculate a match score between 0.0 and 1.0
        and provide a rationale for the score. The output should be in JSON format with the keys "score" and "rationale".

        CV Profile:
        ---
        {cv_profile}
        ---

        Job Description:
        ---
        {job_text}
        ---

        JSON Output:
        """

        try:
            response = self.co.chat(
                model="command-r",
                message=prompt,
                temperature=0.2,
            )
            # Extract the JSON part from the response
            json_text = response.text.strip()
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0]

            import json
            return json.loads(json_text)
        except Exception as e:
            print(f"Error matching job with AI: {e}")
            return {}
