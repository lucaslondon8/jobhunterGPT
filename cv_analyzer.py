#!/usr/bin/env python3
"""
cv_analyzer.py - Universal CV Analysis Engine
Extracts skills, experience, and job targets from ANY CV
"""

import re
from typing import Dict, List, Set, Tuple
from collections import Counter
import os

class UniversalCVAnalyzer:
    def __init__(self):
        # Industry-specific keyword mappings - CALIBRATED FOR BETA USERS
        self.industry_keywords = {
            'devops_cloud': {
                'keywords': ['devops', 'devsecops', 'aws', 'azure', 'kubernetes', 'docker', 'terraform', 
                           'ci/cd', 'jenkins', 'python', 'java', 'gitops', 'monitoring', 'security'],
                'job_sites': ['indeed', 'linkedin', 'remoteok', 'github'],
                'search_terms': ['devops', 'cloud engineer', 'aws', 'kubernetes', 'devsecops'],
                'weight_multiplier': 1.2
            },
            'cybersecurity': {
                'keywords': ['cyber security', 'ethical hacking', 'network security', 'penetration testing',
                           'security analyst', 'risk management', 'compliance', 'vulnerability', 'firewall'],
                'job_sites': ['indeed', 'linkedin', 'cyberjobs', 'remoteok'],
                'search_terms': ['cyber security', 'security analyst', 'ethical hacking', 'penetration testing'],
                'weight_multiplier': 1.2
            },
            'recruitment_hr': {
                'keywords': ['recruitment', 'talent acquisition', 'hr', 'recruiting', 'sourcing', 
                           'employer branding', 'stakeholder management', 'crm', 'talent lead'],
                'job_sites': ['indeed', 'linkedin', 'recruitmentjobs', 'totaljobs'],
                'search_terms': ['recruiter', 'talent acquisition', 'hr', 'recruitment consultant'],
                'weight_multiplier': 1.1
            },
            'healthcare_public_health': {
                'keywords': ['public health', 'healthcare', 'patient safety', 'infection control', 
                           'epidemiology', 'health analytics', 'clinical', 'operating department', 'nhs'],
                'job_sites': ['nhsjobs', 'indeed', 'healthjobsuk', 'linkedin'],
                'search_terms': ['public health', 'healthcare', 'clinical', 'health analyst'],
                'weight_multiplier': 1.1
            },
            'customer_service': {
                'keywords': ['customer service', 'customer support', 'call centre', 'customer experience',
                           'crm', 'customer success', 'support coordination', 'customer advisor'],
                'job_sites': ['indeed', 'totaljobs', 'cv-library', 'linkedin'],
                'search_terms': ['customer service', 'customer support', 'call centre', 'customer success'],
                'weight_multiplier': 1.0
            },
            'content_marketing': {
                'keywords': ['content writing', 'digital marketing', 'seo', 'copywriting', 'social media',
                           'content strategy', 'email marketing', 'analytics', 'adobe', 'cms'],
                'job_sites': ['indeed', 'linkedin', 'marketingjobs', 'remoteok'],
                'search_terms': ['content writer', 'digital marketing', 'copywriter', 'marketing'],
                'weight_multiplier': 1.1
            },
            'operations_management': {
                'keywords': ['operations', 'team leadership', 'project management', 'process improvement',
                           'stakeholder management', 'risk management', 'compliance', 'prince2'],
                'job_sites': ['indeed', 'linkedin', 'totaljobs', 'managementjobs'],
                'search_terms': ['operations manager', 'team leader', 'project manager', 'operations'],
                'weight_multiplier': 1.0
            },
            'finance_accounting': {
                'keywords': ['accounting', 'finance', 'financial analysis', 'fund accountant', 'excel',
                           'financial performance', 'corporate governance', 'esg', 'stata', 'spss'],
                'job_sites': ['indeed', 'linkedin', 'accountancyjobs', 'financejobs'],
                'search_terms': ['accountant', 'finance', 'financial analyst', 'fund accountant'],
                'weight_multiplier': 1.0
            },
            'aviation_transport': {
                'keywords': ['aviation', 'crewing', 'easa ftl', 'crew management', 'airport operations',
                           'scheduling', 'compliance', 'aviation systems', 'airline'],
                'job_sites': ['aviationjobsearch', 'indeed', 'linkedin', 'airlinejob'],
                'search_terms': ['aviation', 'crewing officer', 'airport operations', 'airline'],
                'weight_multiplier': 1.0
            },
            'academic_research': {
                'keywords': ['university', 'lecturer', 'research', 'phd', 'academic writing', 'teaching',
                           'module leadership', 'supervision', 'academia', 'higher education'],
                'job_sites': ['jobs.ac.uk', 'timeshighereducation', 'indeed', 'linkedin'],
                'search_terms': ['university lecturer', 'academic', 'research', 'higher education'],
                'weight_multiplier': 1.0
            },
            'care_support': {
                'keywords': ['care work', 'support work', 'healthcare assistant', 'safeguarding',
                           'first aid', 'care management', 'support coordination', 'carer'],
                'job_sites': ['carejobs', 'indeed', 'totaljobs', 'cv-library'],
                'search_terms': ['care worker', 'support worker', 'healthcare assistant', 'carer'],
                'weight_multiplier': 1.0
            },
            'sales_business_development': {
                'keywords': ['sales', 'business development', 'sales support', 'account management',
                           'sales coordinator', 'kpi tracking', 'sales ambassador'],
                'job_sites': ['indeed', 'linkedin', 'salesjobs', 'totaljobs'],
                'search_terms': ['sales', 'business development', 'account manager', 'sales coordinator'],
                'weight_multiplier': 1.0
            }
        }
        
        # Experience level patterns
        self.experience_patterns = {
            'junior': ['junior', 'entry level', '0-2 years', 'graduate', 'intern', 'trainee'],
            'mid': ['2-5 years', '3-6 years', 'mid level', 'intermediate', 'associate'],
            'senior': ['senior', '5+ years', '6+ years', 'lead', 'principal', 'expert'],
            'executive': ['cto', 'ceo', 'vp', 'director', 'head of', 'chief', '10+ years']
        }
        
        # Job title patterns
        self.job_title_patterns = {
            'engineer': ['engineer', 'developer', 'programmer', 'coder'],
            'analyst': ['analyst', 'researcher', 'scientist'],
            'manager': ['manager', 'lead', 'director', 'head'],
            'designer': ['designer', 'ui/ux', 'creative'],
            'consultant': ['consultant', 'advisor', 'specialist']
        }

    def analyze_cv(self, cv_text: str) -> Dict:
        """
        Analyze any CV and return comprehensive profile information
        CALIBRATED FOR BETA USER PROFILES
        """
        cv_lower = cv_text.lower()
        
        # Extract basic information
        skills = self._extract_skills(cv_text)
        experience_level = self._determine_experience_level(cv_text)
        industries = self._identify_industries(skills, cv_text)
        job_types = self._identify_job_types(cv_text)
        
        # DYNAMIC: Extract user profile patterns from CV content
        user_profile = self._extract_dynamic_profile(cv_text, skills, experience_level)
        
        # Determine primary industry focus
        primary_industry = self._get_primary_industry(industries)
        
        # Generate job search strategy
        search_strategy = self._generate_search_strategy(primary_industry, skills, experience_level, user_profile)
        
        # Calculate skill weights for matching
        skill_weights = self._calculate_skill_weights(skills, primary_industry)
        
        return {
            'skills': skills,
            'experience_level': experience_level,
            'industries': industries,
            'primary_industry': primary_industry,
            'job_types': job_types,
            'search_strategy': search_strategy,
            'skill_weights': skill_weights,
            'user_profile': user_profile,
            'cv_length': len(cv_text),
            'analysis_confidence': self._calculate_confidence(skills, industries)
        }

    def _extract_dynamic_profile(self, cv_text: str, skills: List[str], experience_level: str) -> Dict:
        """
        DYNAMICALLY extract user profile patterns from CV content
        NO HARDCODED USERS - Pure dynamic analysis
        """
        cv_lower = cv_text.lower()
        
        # Dynamic skill clustering
        skill_clusters = {
            'technical_advanced': ['kubernetes', 'terraform', 'aws', 'azure', 'docker', 'ci/cd', 'devsecops'],
            'security_focused': ['cyber security', 'ethical hacking', 'penetration testing', 'vulnerability'],
            'people_management': ['recruitment', 'talent acquisition', 'team leadership', 'stakeholder management'],
            'creative_content': ['content writing', 'marketing', 'seo', 'copywriting', 'social media'],
            'healthcare_clinical': ['public health', 'patient safety', 'clinical', 'healthcare', 'infection control'],
            'customer_facing': ['customer service', 'customer support', 'call centre', 'customer experience'],
            'operations_process': ['operations', 'project management', 'process improvement', 'compliance'],
            'financial_analysis': ['accounting', 'finance', 'financial analysis', 'fund accountant'],
            'aviation_transport': ['aviation', 'crewing', 'airport operations', 'crew management'],
            'academic_research': ['university', 'lecturer', 'research', 'phd', 'academic'],
            'care_support': ['care work', 'support worker', 'healthcare assistant', 'safeguarding'],
            'early_career': ['gcse', 'entry level', 'graduate', 'trainee', 'part-time']
        }
        
        # Score each cluster dynamically
        cluster_scores = {}
        for cluster_name, cluster_keywords in skill_clusters.items():
            matches = sum(1 for keyword in cluster_keywords if keyword in cv_lower)
            if matches > 0:
                cluster_scores[cluster_name] = {
                    'score': matches / len(cluster_keywords),
                    'matched_count': matches,
                    'keywords': [kw for kw in cluster_keywords if kw in cv_lower]
                }
        
        # Determine primary profile dynamically
        if cluster_scores:
            primary_cluster = max(cluster_scores.items(), key=lambda x: x[1]['score'])
            profile_type = primary_cluster[0]
            confidence = primary_cluster[1]['score']
        else:
            profile_type = 'general_professional'
            confidence = 0.3
        
        # Dynamic seniority detection
        seniority_indicators = {
            'leadership': ['lead', 'senior', 'principal', 'head of', 'director', 'manager'],
            'expertise': ['expert', 'specialist', 'consultant', 'architect'],
            'experience_years': re.findall(r'(\d+)\+?\s*years?', cv_lower)
        }
        
        leadership_score = sum(1 for term in seniority_indicators['leadership'] if term in cv_lower)
        expertise_score = sum(1 for term in seniority_indicators['expertise'] if term in cv_lower)
        
        return {
            'profile_type': profile_type,
            'confidence': confidence,
            'skill_clusters': cluster_scores,
            'leadership_score': leadership_score,
            'expertise_score': expertise_score,
            'is_senior': leadership_score > 0 or expertise_score > 0,
            'specialization_depth': len([cluster for cluster, data in cluster_scores.items() if data['score'] > 0.3])
        }

    def _extract_skills(self, cv_text: str) -> List[str]:
        """Extract technical skills from CV"""
        cv_lower = cv_text.lower()
        all_skills = set()
        
        # Extract from all industry categories
        for industry_data in self.industry_keywords.values():
            for keyword in industry_data['keywords']:
                if keyword.lower() in cv_lower:
                    all_skills.add(keyword)
        
        # Extract additional skills using patterns
        skill_patterns = [
            r'\b(python|java|javascript|typescript|c\+\+|c#|ruby|go|rust|php)\b',
            r'\b(react|angular|vue|django|flask|spring|express|laravel)\b',
            r'\b(aws|azure|gcp|docker|kubernetes|terraform|jenkins)\b',
            r'\b(mysql|postgresql|mongodb|redis|elasticsearch)\b',
            r'\b(git|github|gitlab|bitbucket|jira|confluence)\b'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, cv_lower, re.IGNORECASE)
            all_skills.update(matches)
        
        return list(all_skills)

    def _determine_experience_level(self, cv_text: str) -> str:
        """Determine experience level from CV"""
        cv_lower = cv_text.lower()
        
        # Count experience indicators
        level_scores = {level: 0 for level in self.experience_patterns.keys()}
        
        for level, patterns in self.experience_patterns.items():
            for pattern in patterns:
                if pattern in cv_lower:
                    level_scores[level] += 1
        
        # Extract years of experience
        year_matches = re.findall(r'(\d+)\+?\s*years?\s+(?:of\s+)?experience', cv_lower)
        if year_matches:
            max_years = max(int(year) for year in year_matches)
            if max_years >= 8:
                level_scores['senior'] += 2
            elif max_years >= 4:
                level_scores['mid'] += 2
            else:
                level_scores['junior'] += 2
        
        # Return highest scoring level
        return max(level_scores.items(), key=lambda x: x[1])[0]

    def _identify_industries(self, skills: List[str], cv_text: str) -> Dict[str, float]:
        """Identify relevant industries based on skills and CV content"""
        industry_scores = {}
        cv_lower = cv_text.lower()
        
        for industry, data in self.industry_keywords.items():
            score = 0
            matched_keywords = 0
            
            for keyword in data['keywords']:
                if keyword.lower() in cv_lower:
                    # Different weights for different keyword importance
                    if keyword.lower() in ['solidity', 'blockchain', 'tensorflow', 'react']:
                        score += 3  # High-value keywords
                    else:
                        score += 1
                    matched_keywords += 1
            
            # Normalize score by total keywords in industry
            if matched_keywords > 0:
                normalized_score = score / len(data['keywords'])
                industry_scores[industry] = {
                    'score': normalized_score,
                    'matched_keywords': matched_keywords,
                    'confidence': min(normalized_score * 2, 1.0)
                }
        
        return industry_scores

    def _identify_job_types(self, cv_text: str) -> List[str]:
        """Identify potential job types/roles"""
        cv_lower = cv_text.lower()
        job_types = []
        
        for job_type, patterns in self.job_title_patterns.items():
            for pattern in patterns:
                if pattern in cv_lower:
                    job_types.append(job_type)
                    break
        
        return job_types

    def _get_primary_industry(self, industries: Dict[str, Dict]) -> str:
        """Determine primary industry focus"""
        if not industries:
            return 'general_tech'
        
        # Return industry with highest confidence score
        primary = max(industries.items(), key=lambda x: x[1]['confidence'])
        return primary[0]

    def _generate_search_strategy(self, primary_industry: str, skills: List[str], 
                                experience_level: str, user_profile: Dict = None) -> Dict:
        """
        Generate job search strategy based on analysis
        ENHANCED FOR BETA USER PATTERNS
        """
        if primary_industry not in self.industry_keywords:
            primary_industry = 'customer_service'  # Default for many beta users
        
        industry_data = self.industry_keywords.get(primary_industry, {})
        
        # Beta user specific job site targeting
        enhanced_sites = industry_data.get('job_sites', ['indeed', 'linkedin'])
        
        # Add UK-specific sites (most beta users are UK-based)
        uk_sites = ['totaljobs', 'cv-library', 'reed.co.uk']
        enhanced_sites.extend([site for site in uk_sites if site not in enhanced_sites])
        
        # Enhanced keywords based on beta user patterns
        search_keywords = industry_data.get('search_terms', skills[:4])
        
        # Add location-specific terms (London, Manchester, etc.)
        location_keywords = ['london', 'manchester', 'remote uk', 'hybrid']
        
        return {
            'target_job_sites': enhanced_sites,
            'search_keywords': search_keywords,
            'location_keywords': location_keywords,
            'experience_modifiers': [experience_level],
            'priority_skills': skills[:5],
            'beta_user_type': user_profile.get('profile_type', 'general') if user_profile else 'general',
            'recommended_filters': {
                'experience_level': experience_level,
                'remote_friendly': True,
                'uk_focused': True,  # Most beta users are UK-based
                'industry_focus': primary_industry,
                'salary_range': self._get_salary_range(experience_level, primary_industry)
            }
        }

    def _get_salary_range(self, experience_level: str, industry: str) -> Dict:
        """Get appropriate salary range for UK market"""
        base_ranges = {
            'junior': {'min': 20000, 'max': 35000},
            'mid': {'min': 35000, 'max': 55000},
            'senior': {'min': 55000, 'max': 85000},
            'executive': {'min': 80000, 'max': 150000}
        }
        
        # Industry multipliers for UK market
        multipliers = {
            'devops_cloud': 1.3,
            'cybersecurity': 1.2,
            'recruitment_hr': 1.0,
            'healthcare_public_health': 0.9,
            'content_marketing': 1.1,
            'finance_accounting': 1.1,
            'aviation_transport': 1.0,
            'academic_research': 0.8,
            'customer_service': 0.8,
            'operations_management': 1.0
        }
        
        base = base_ranges.get(experience_level, base_ranges['mid'])
        multiplier = multipliers.get(industry, 1.0)
        
        return {
            'min': int(base['min'] * multiplier),
            'max': int(base['max'] * multiplier),
            'currency': 'GBP'
        }

    def _calculate_skill_weights(self, skills: List[str], primary_industry: str) -> Dict[str, float]:
        """Calculate skill weights for job matching"""
        weights = {}
        
        if primary_industry in self.industry_keywords:
            industry_keywords = self.industry_keywords[primary_industry]['keywords']
            multiplier = self.industry_keywords[primary_industry]['weight_multiplier']
            
            for skill in skills:
                if skill.lower() in [k.lower() for k in industry_keywords]:
                    # High weight for industry-specific skills
                    weights[skill] = 4.0 * multiplier
                else:
                    # Lower weight for general skills
                    weights[skill] = 2.0
        else:
            # Default weights for unknown industries
            for skill in skills:
                weights[skill] = 2.5
        
        return weights

    def _calculate_confidence(self, skills: List[str], industries: Dict) -> float:
        """Calculate overall analysis confidence"""
        if not skills or not industries:
            return 0.1
        
        # Base confidence on number of skills and industry matches
        skill_confidence = min(len(skills) / 10, 1.0)  # Up to 10 skills = full confidence
        
        if industries:
            industry_confidence = max(ind['confidence'] for ind in industries.values())
        else:
            industry_confidence = 0.1
        
        return (skill_confidence + industry_confidence) / 2


def analyze_any_cv(cv_text: str) -> Dict:
    """
    Main function to analyze any CV and return adaptive job search parameters
    """
    analyzer = UniversalCVAnalyzer()
    return analyzer.analyze_cv(cv_text)


def get_adaptive_search_params(cv_analysis: Dict) -> Dict:
    """
    Convert CV analysis into search parameters for job discovery
    """
    return {
        'target_sites': cv_analysis['search_strategy']['target_job_sites'],
        'search_keywords': cv_analysis['search_strategy']['search_keywords'],
        'skill_weights': cv_analysis['skill_weights'],
        'experience_level': cv_analysis['experience_level'],
        'primary_industry': cv_analysis['primary_industry'],
        'confidence': cv_analysis['analysis_confidence']
    }


if __name__ == "__main__":
    # Test with DYNAMIC CV ANALYSIS (No hardcoded users!)
    
    # Test 1: DevSecOps Professional
    test_devops_cv = """
    Lead DevSecOps Engineer
    8+ years experience in cloud infrastructure and security
    Skills: AWS, Azure, Kubernetes, Docker, Terraform, CI/CD, Jenkins, Python, Java, Security, Monitoring, GitOps
    BTech Computer Science, AWS/Azure/Kubernetes certified
    Location: UK
    """
    
    # Test 2: Content Marketing Professional  
    test_marketing_cv = """
    Senior Digital Marketing Specialist
    Skills: Content Writing, Digital Marketing, SEO, Social Media Management, Copy Writing, Analytics, Adobe Photoshop, Canva, CMS, Blog Writing, Email Marketing
    BA Media and English (2:1), Teaching Qualification
    Experience: Digital Content Editor, Senior Copywriter, Freelance Editor/Author
    Location: UK
    """
    
    # Test 3: Tech Recruitment Professional
    test_recruitment_cv = """
    Global Talent Acquisition Lead
    Skills: Recruitment, HR, Talent Acquisition, Employer Branding, Stakeholder Management, Video Editing, Content Creation, Automation, CRM, Data Management
    Experience: Global Talent Lead, Senior Recruiter, Technology Recruiter, Recruitment Business Partner
    Specialization: Tech Recruitment, Start-up Scaling
    Location: Remote, London
    """
    
    # Test 4: Early Career Professional
    test_early_career_cv = """
    Graduate seeking opportunities
    Skills: Teamwork, Communication, Fast Learning, Tutoring, Customer Service, Retail
    Experience: Part-time retail, Tutoring  
    Education: 7 GCSEs including Maths, English, Science
    Career Stage: Entry level, seeking opportunities
    Location: London
    """
    
    analyzer = UniversalCVAnalyzer()
    
    print("=== DYNAMIC CV ANALYSIS (No Hardcoded Users) ===")
    
    test_cases = [
        ("DevSecOps Professional", test_devops_cv),
        ("Content Marketing Professional", test_marketing_cv), 
        ("Tech Recruitment Professional", test_recruitment_cv),
        ("Early Career Professional", test_early_career_cv)
    ]
    
    for name, cv_text in test_cases:
        print(f"\n--- {name} ---")
        analysis = analyzer.analyze_cv(cv_text)
        print(f"Primary Industry: {analysis['primary_industry']}")
        print(f"Experience Level: {analysis['experience_level']}")
        print(f"Dynamic Profile: {analysis['user_profile']['profile_type']}")
        print(f"Profile Confidence: {analysis['user_profile']['confidence']:.2f}")
        print(f"Is Senior: {analysis['user_profile']['is_senior']}")
        print(f"Top Skills: {analysis['skills'][:5]}")
        print(f"Target Sites: {analysis['search_strategy']['target_job_sites'][:3]}")
        print(f"Search Keywords: {analysis['search_strategy']['search_keywords']}")
        print(f"Salary Range: £{analysis['search_strategy']['recommended_filters']['salary_range']['min']:,} - £{analysis['search_strategy']['recommended_filters']['salary_range']['max']:,}")
        print(f"Overall Confidence: {analysis['analysis_confidence']:.2f}")
        print("---")
