# analyzer/cv_analyzer.py

import re
from typing import List, Dict

def _generate_search_keywords(analysis: Dict) -> List[str]:
    """
    Internal function to generate targeted search keywords based on CV analysis.
    """
    keywords = set()
    industry = analysis.get('industry_category')
    experience = analysis.get('experience_level')
    roles = analysis.get('specific_roles', [])[:5]      # Use top 5 roles
    skills = analysis.get('technical_skills', [])[:5]  # Use top 5 skills

    # Use the most specific roles as the base for keywords
    base_keywords = roles if roles else [industry.replace('_', ' ')] if industry else ['jobs']
    
    # Add experience level prefixes to the base keywords
    if experience == 'senior':
        for keyword in base_keywords:
            keywords.add(f"senior {keyword}")
            keywords.add(f"lead {keyword}")
    elif experience == 'junior':
        for keyword in base_keywords:
            keywords.add(f"junior {keyword}")
            keywords.add(f"graduate {keyword}")
    else:
        for keyword in base_keywords:
            keywords.add(keyword)
    
    # Add skill-based searches for more targeted results
    for skill in skills:
        keywords.add(f"{skill} jobs")
        
    return list(keywords)[:15] # Return up to 15 unique keywords

def analyze_cv_for_search(cv_text: str) -> Dict:
    """
    Analyzes CV text to determine industry, experience, and skills,
    then generates targeted search keywords.
    """
    if not cv_text:
        return {}

    cv_lower = cv_text.lower()
    
    analysis = {
        'industry_category': 'general',
        'specific_roles': [],
        'technical_skills': [],
        'soft_skills': [],
        'experience_level': 'mid',
        'location_preferences': [],
        'search_keywords': []
    }
    
    # Define keywords to detect industry from the CV
    industry_patterns = {
        'tech_cloud_security': ['devops', 'devsecops', 'cloud', 'aws', 'azure', 'gcp', 'kubernetes', 'cybersecurity', 'terraform', 'docker'],
        'web3_blockchain': ['web3', 'blockchain', 'defi', 'ethereum', 'solidity', 'smart contract', 'nft', 'dao'],
        'recruitment_hr': ['recruitment', 'talent acquisition', 'sourcing', 'ats', 'recruiter', 'hiring'],
        'finance_accounting': ['fund accountant', 'financial analyst', 'accounting', 'audit', 'compliance', 'finance', 'trading', 'fintech'],
        'sales_business_development': ['sales', 'business development', 'crm', 'pipeline', 'revenue', 'clients'],
        'design_creative': ['designer', 'ui/ux', 'figma', 'sketch', 'adobe xd', 'creative'],
        # Add more industry patterns as needed
    }

    # Detect the primary industry based on keyword frequency
    industry_scores = {
        industry: sum(1 for keyword in keywords if keyword in cv_lower)
        for industry, keywords in industry_patterns.items()
    }
    if any(score > 0 for score in industry_scores.values()):
        analysis['industry_category'] = max(industry_scores, key=industry_scores.get)

    # Expanded regex for roles and skills
    roles_pattern = r'\b(software engineer|engineer|developer|analyst|manager|recruiter|accountant|specialist|coordinator|consultant|architect|designer|producer|strategist|administrator|associate|officer|executive|head|director|lead)\b'
    tech_skills_pattern = r'\b(python|javascript|java|c\+\+|c\#|go|rust|solidity|vyper|ruby|php|swift|kotlin|typescript|react|angular|vue|node\.js|django|flask|fastapi|aws|azure|gcp|docker|kubernetes|linux|sql|mongodb|postgresql|mysql|redis|git|jira|scrum|agile|ci/cd|terraform|ethers\.js|web3\.js|hardhat|truffle|foundry|salesforce|excel)\b'
    soft_skills_pattern = r'\b(communication|teamwork|problem-solving|leadership|management|collaboration|adaptability|creativity)\b'

    analysis['specific_roles'] = list(set(re.findall(roles_pattern, cv_lower)))
    analysis['technical_skills'] = list(set(re.findall(tech_skills_pattern, cv_lower)))
    analysis['soft_skills'] = list(set(re.findall(soft_skills_pattern, cv_lower)))

    # Determine experience level
    if any(word in cv_lower for word in ['senior', 'lead', 'principal', 'head of', 'director', 'manager']):
        analysis['experience_level'] = 'senior'
    elif any(word in cv_lower for word in ['junior', 'graduate', 'entry-level', 'intern', 'assistant']):
        analysis['experience_level'] = 'junior'

    # Generate the final search keywords based on the analysis
    analysis['search_keywords'] = _generate_search_keywords(analysis)
    
    return analysis
