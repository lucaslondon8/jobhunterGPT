#!/usr/bin/env python3
"""
matcher/match_job.py - Real CV-Job Matching Algorithm
Implements intelligent matching between your CV and real job descriptions
"""

import re
from typing import List, Dict, Set, Tuple
from collections import Counter
import math
import os

class RealJobMatcher:
    """Real CV-Job matching system with industry-standard algorithms"""
    
    def __init__(self):
        # Web3 and blockchain keywords with realistic weights
        self.web3_keywords = {
            'web3': 4.0, 'blockchain': 4.0, 'defi': 4.5, 'ethereum': 3.5,
            'smart contract': 4.0, 'smart contracts': 4.0, 'solidity': 4.5,
            'crypto': 2.5, 'cryptocurrency': 2.5, 'dapp': 3.0, 'dapps': 3.0,
            'flash loan': 5.0, 'flash loans': 5.0, 'mev': 4.0, 'dao': 2.5,
            'nft': 2.0, 'polygon': 2.5, 'chainlink': 2.5, 'uniswap': 3.0,
            'aave': 3.0, 'compound': 3.0, 'liquidity': 2.5, 'yield farming': 3.5,
            'automated market maker': 3.5, 'amm': 3.5, 'liquidation': 4.0,
            'metamask': 2.5, 'web3.js': 3.5, 'ethers.js': 3.5, 'ipfs': 2.5,
            'consensus': 2.0, 'protocol': 2.0, 'tokenomics': 2.5
        }
        
        # Technical skills with market relevance weights
        self.tech_keywords = {
            'python': 3.0, 'javascript': 2.5, 'node.js': 2.5, 'nodejs': 2.5,
            'react': 2.0, 'typescript': 2.2, 'fastapi': 2.5, 'express': 2.0,
            'api': 1.5, 'rest': 1.5, 'restful': 1.5, 'backend': 2.0,
            'frontend': 1.8, 'full stack': 2.5, 'fullstack': 2.5,
            'git': 1.2, 'docker': 1.8, 'aws': 1.8, 'linux': 1.5,
            'mongodb': 1.5, 'postgresql': 1.5, 'mysql': 1.3, 'redis': 1.5,
            'kubernetes': 2.0, 'microservices': 2.0, 'graphql': 1.8
        }
        
        # Experience and role keywords
        self.experience_keywords = {
            'senior': 2.5, 'lead': 2.8, 'principal': 3.0, 'staff': 2.6,
            'architect': 2.5, 'engineer': 2.0, 'developer': 2.0,
            'cto': 3.5, 'technical lead': 2.8, 'team lead': 2.5,
            'startup': 2.2, 'entrepreneur': 2.5, 'founder': 3.0,
            'remote': 1.5, 'freelance': 1.3, 'contract': 1.2
        }
        
        # Industry-specific bonus keywords
        self.industry_keywords = {
            'fintech': 2.0, 'financial': 1.8, 'trading': 2.2, 'exchange': 2.5,
            'payments': 1.8, 'banking': 1.5, 'investment': 1.7,
            'security': 2.0, 'audit': 2.2, 'compliance': 1.5
        }
        
        # Stop words to ignore in matching
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'should', 'could', 'can', 'may', 'might',
            'this', 'that', 'these', 'those', 'we', 'you', 'they', 'it',
            'job', 'role', 'position', 'candidate', 'experience', 'work',
            'looking', 'seeking', 'required', 'preferred', 'must', 'nice'
        }
    
    def clean_and_tokenize(self, text: str) -> List[str]:
        """Clean and tokenize text for matching"""
        if not text:
            return []
        
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s\.\-]', ' ', text.lower())
        
        # Split into words and filter
        words = text.split()
        
        # Remove stop words and short words
        filtered_words = [
            word for word in words 
            if len(word) > 2 and word not in self.stop_words
        ]
        
        return filtered_words
    
    def extract_phrases(self, text: str) -> Set[str]:
        """Extract important multi-word phrases"""
        phrases = set()
        text_lower = text.lower()
        
        # Important multi-word phrases to detect
        important_phrases = [
            'smart contract', 'smart contracts', 'flash loan', 'flash loans',
            'yield farming', 'automated market maker', 'full stack', 'fullstack',
            'technical lead', 'team lead', 'node.js', 'web3.js', 'ethers.js',
            'machine learning', 'artificial intelligence', 'data science',
            'cloud computing', 'software engineering'
        ]
        
        for phrase in important_phrases:
            if phrase in text_lower:
                phrases.add(phrase)
        
        return phrases
    
    def calculate_keyword_scores(self, cv_text: str, job_text: str) -> Dict[str, float]:
        """Calculate weighted keyword scores for different categories"""
        cv_clean = cv_text.lower()
        job_clean = job_text.lower()
        
        scores = {
            'web3_score': 0.0,
            'tech_score': 0.0,
            'experience_score': 0.0,
            'industry_score': 0.0
        }
        
        # Calculate scores for each category
        keyword_categories = [
            ('web3_score', self.web3_keywords),
            ('tech_score', self.tech_keywords),
            ('experience_score', self.experience_keywords),
            ('industry_score', self.industry_keywords)
        ]
        
        for score_key, keywords_dict in keyword_categories:
            for keyword, weight in keywords_dict.items():
                cv_count = cv_clean.count(keyword)
                job_count = job_clean.count(keyword)
                
                if cv_count > 0 and job_count > 0:
                    # Score based on presence and frequency
                    score_contribution = weight * min(cv_count, job_count) * 0.5
                    scores[score_key] += score_contribution
        
        # Normalize scores to 0-1 range
        max_scores = {
            'web3_score': 20.0,  # Max possible Web3 score
            'tech_score': 15.0,  # Max possible tech score
            'experience_score': 10.0,  # Max possible experience score
            'industry_score': 8.0   # Max possible industry score
        }
        
        for key in scores:
            scores[key] = min(1.0, scores[key] / max_scores[key])
        
        return scores
    
    def calculate_text_similarity(self, cv_text: str, job_text: str) -> float:
        """Calculate text similarity using term frequency approach"""
        try:
            cv_words = self.clean_and_tokenize(cv_text)
            job_words = self.clean_and_tokenize(job_text)
            
            if not cv_words or not job_words:
                return 0.0
            
            # Create word frequency vectors
            all_words = set(cv_words + job_words)
            
            cv_freq = {word: cv_words.count(word) for word in all_words}
            job_freq = {word: job_words.count(word) for word in all_words}
            
            # Calculate cosine similarity
            dot_product = sum(cv_freq[word] * job_freq[word] for word in all_words)
            cv_magnitude = math.sqrt(sum(cv_freq[word] ** 2 for word in all_words))
            job_magnitude = math.sqrt(sum(job_freq[word] ** 2 for word in all_words))
            
            if cv_magnitude == 0 or job_magnitude == 0:
                return 0.0
            
            similarity = dot_product / (cv_magnitude * job_magnitude)
            return min(1.0, similarity)
            
        except Exception as e:
            print(f"❌ Error calculating similarity: {e}")
            return 0.0
    
    def calculate_phrase_bonus(self, cv_text: str, job_text: str) -> float:
        """Calculate bonus score for matching important phrases"""
        cv_phrases = self.extract_phrases(cv_text)
        job_phrases = self.extract_phrases(job_text)
        
        if not cv_phrases or not job_phrases:
            return 0.0
        
        matching_phrases = cv_phrases.intersection(job_phrases)
        phrase_score = len(matching_phrases) / max(len(job_phrases), 1)
        
        return min(0.2, phrase_score)  # Max 20% bonus
    
    def detect_job_level(self, job_text: str) -> str:
        """Detect job seniority level"""
        job_lower = job_text.lower()
        
        if any(word in job_lower for word in ['senior', 'sr.', 'lead', 'principal', 'staff']):
            return 'senior'
        elif any(word in job_lower for word in ['junior', 'jr.', 'entry', 'graduate', 'intern']):
            return 'junior'
        elif any(word in job_lower for word in ['cto', 'director', 'head of', 'vp', 'chief']):
            return 'executive'
        else:
            return 'mid'
    
    def calculate_location_match(self, cv_preferences: str, job_location: str) -> float:
        """Calculate location compatibility score"""
        cv_lower = cv_preferences.lower()
        job_lower = job_location.lower()
        
        # Remote work preference bonus
        if 'remote' in cv_lower and 'remote' in job_lower:
            return 1.0
        
        # UK/Europe preference
        uk_terms = ['uk', 'united kingdom', 'london', 'manchester', 'edinburgh', 'britain']
        europe_terms = ['europe', 'european', 'eu']
        
        cv_wants_uk = any(term in cv_lower for term in uk_terms)
        cv_wants_europe = any(term in cv_lower for term in europe_terms)
        
        job_in_uk = any(term in job_lower for term in uk_terms)
        job_in_europe = any(term in job_lower for term in europe_terms)
        
        if cv_wants_uk and job_in_uk:
            return 0.9
        elif cv_wants_europe and (job_in_uk or job_in_europe):
            return 0.8
        elif 'remote' in job_lower:
            return 0.7
        else:
            return 0.3

def match_score(cv_text: str, job_text: str) -> float:
    """
    Main matching function - calculates overall match score between CV and job
    Returns score between 0.0 and 1.0 based on real-world factors
    """
    if not cv_text or not job_text:
        return 0.0
    
    matcher = RealJobMatcher()
    
    # Calculate different scoring components
    keyword_scores = matcher.calculate_keyword_scores(cv_text, job_text)
    text_similarity = matcher.calculate_text_similarity(cv_text, job_text)
    phrase_bonus = matcher.calculate_phrase_bonus(cv_text, job_text)
    location_match = matcher.calculate_location_match(cv_text, job_text)
    
    # Weight the different components realistically
    final_score = (
        keyword_scores['web3_score'] * 0.35 +      # Web3 relevance most important
        keyword_scores['tech_score'] * 0.25 +      # Technical skills
        keyword_scores['experience_score'] * 0.15 + # Experience level
        keyword_scores['industry_score'] * 0.10 +   # Industry knowledge
        text_similarity * 0.10 +                    # General text match
        phrase_bonus * 0.05                         # Phrase matching bonus
    )
    
    # Apply location multiplier
    final_score *= (0.7 + 0.3 * location_match)
    
    # Ensure score is between 0 and 1
    return min(1.0, max(0.0, final_score))

def analyze_match(cv_text: str, job_text: str) -> Dict[str, any]:
    """
    Detailed match analysis with actionable insights
    Returns comprehensive analysis for decision making
    """
    matcher = RealJobMatcher()
    
    # Calculate all components
    keyword_scores = matcher.calculate_keyword_scores(cv_text, job_text)
    overall_score = match_score(cv_text, job_text)
    job_level = matcher.detect_job_level(job_text)
    
    # Extract matching and missing keywords
    cv_words = set(matcher.clean_and_tokenize(cv_text))
    job_words = set(matcher.clean_and_tokenize(job_text))
    matching_keywords = cv_words.intersection(job_words)
    
    # Find important missing keywords
    important_job_keywords = set()
    for keyword in matcher.web3_keywords.keys():
        if keyword in job_text.lower():
            important_job_keywords.add(keyword)
    
    missing_important = important_job_keywords - set(cv_text.lower().split())
    
    # Generate analysis
    analysis = {
        'overall_score': round(overall_score, 3),
        'score_breakdown': {
            'web3_relevance': round(keyword_scores['web3_score'], 3),
            'technical_skills': round(keyword_scores['tech_score'], 3),
            'experience_match': round(keyword_scores['experience_score'], 3),
            'industry_knowledge': round(keyword_scores['industry_score'], 3)
        },
        'job_level': job_level,
        'matching_keywords': list(matching_keywords)[:10],  # Top 10
        'missing_keywords': list(missing_important)[:5],     # Top 5 missing
        'match_strength': get_match_strength(overall_score),
        'recommendations': generate_real_recommendations(overall_score, keyword_scores, missing_important, job_level),
        'application_priority': get_application_priority(overall_score, keyword_scores)
    }
    
    return analysis

def get_match_strength(score: float) -> str:
    """Get human-readable match strength"""
    if score >= 0.8:
        return 'Excellent'
    elif score >= 0.6:
        return 'Strong'
    elif score >= 0.4:
        return 'Good'
    elif score >= 0.2:
        return 'Fair'
    else:
        return 'Weak'

def get_application_priority(score: float, keyword_scores: Dict[str, float]) -> str:
    """Determine application priority"""
    if score >= 0.7 and keyword_scores['web3_score'] >= 0.5:
        return 'High'
    elif score >= 0.5:
        return 'Medium'
    elif score >= 0.3:
        return 'Low'
    else:
        return 'Skip'

def generate_real_recommendations(overall_score: float, keyword_scores: Dict[str, float], 
                                missing_keywords: set, job_level: str) -> List[str]:
    """Generate actionable recommendations"""
    recommendations = []
    
    # Score-based recommendations
    if overall_score >= 0.7:
        recommendations.append("🎯 Excellent match! Apply immediately and prioritize this role")
        recommendations.append("💼 Tailor your cover letter to highlight Web3 experience")
    elif overall_score >= 0.5:
        recommendations.append("✅ Good match - worth applying with customized application")
    elif overall_score >= 0.3:
        recommendations.append("⚠️ Moderate match - consider if you want to expand skillset")
    else:
        recommendations.append("❌ Poor match - better to focus on more relevant opportunities")
    
    # Skill-specific recommendations
    if keyword_scores['web3_score'] < 0.3:
        recommendations.append("🔧 Highlight your DeFi and smart contract experience more prominently")
    
    if keyword_scores['tech_score'] < 0.4:
        recommendations.append("💻 Emphasize your Python, JavaScript, and backend development skills")
    
    # Missing keywords recommendations
    if missing_keywords:
        missing_str = ', '.join(list(missing_keywords)[:3])
        recommendations.append(f"📚 Consider mentioning: {missing_str}")
    
    # Level-specific advice
    if job_level == 'senior' and keyword_scores['experience_score'] < 0.5:
        recommendations.append("🎖️ Emphasize your leadership and senior-level project experience")
    elif job_level == 'executive':
        recommendations.append("👔 Highlight your entrepreneurial experience and startup scaling")
    
    return recommendations

# Utility functions for batch processing real jobs

def batch_match_jobs(cv_text: str, jobs_list: List[Dict]) -> List[Dict]:
    """Match CV against multiple real jobs and return scored results"""
    
    print(f"🎯 Matching CV against {len(jobs_list)} real jobs...")
    
    for i, job in enumerate(jobs_list):
        try:
            # Combine job fields for matching
            job_text = f"{job.get('title', '')} {job.get('company', '')} {job.get('description', '')} {job.get('tags', '')}"
            
            # Calculate match score
            job['match_score'] = match_score(cv_text, job_text)
            job['match_analysis'] = analyze_match(cv_text, job_text)
            
            # Add derived fields
            job['combined_score'] = job['match_score']  # For compatibility
            job['score'] = job['match_score']           # For compatibility
            
            if (i + 1) % 10 == 0:
                print(f"✅ Processed {i + 1}/{len(jobs_list)} jobs")
                
        except Exception as e:
            print(f"❌ Error matching job {i+1}: {e}")
            job['match_score'] = 0.0
            job['combined_score'] = 0.0
            job['score'] = 0.0
    
    # Sort by match score descending
    jobs_list.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    
    print(f"🏆 Top match: {jobs_list[0]['title']} at {jobs_list[0]['company']} ({jobs_list[0]['match_score']:.3f})")
    
    return jobs_list

def filter_jobs_by_score(jobs_list: List[Dict], min_score: float = 0.2) -> List[Dict]:
    """Filter jobs by minimum match score - realistic threshold"""
    filtered = [job for job in jobs_list if job.get('match_score', 0) >= min_score]
    print(f"🔍 Filtered to {len(filtered)} jobs above {min_score:.1f} match score")
    return filtered

def get_top_matches(jobs_list: List[Dict], top_n: int = 20) -> List[Dict]:
    """Get top N job matches for application"""
    sorted_jobs = sorted(jobs_list, key=lambda x: x.get('match_score', 0), reverse=True)
    top_jobs = sorted_jobs[:top_n]
    
    print(f"🎯 Top {len(top_jobs)} matches selected for applications")
    for i, job in enumerate(top_jobs[:5]):
        print(f"   {i+1}. {job['title']} at {job['company']} - {job['match_score']:.3f}")
    
    return top_jobs

def analyze_job_market(jobs_list: List[Dict]) -> Dict[str, any]:
    """Analyze the job market from scraped data"""
    
    if not jobs_list:
        return {}
    
    # Calculate market insights
    scores = [job.get('match_score', 0) for job in jobs_list]
    companies = [job.get('company', 'Unknown') for job in jobs_list]
    locations = [job.get('location', 'Unknown') for job in jobs_list]
    
    analysis = {
        'total_jobs': len(jobs_list),
        'avg_match_score': sum(scores) / len(scores) if scores else 0,
        'high_match_count': len([s for s in scores if s >= 0.6]),
        'top_companies': Counter(companies).most_common(5),
        'top_locations': Counter(locations).most_common(5),
        'market_insights': generate_market_insights(jobs_list)
    }
    
    return analysis

def generate_market_insights(jobs_list: List[Dict]) -> List[str]:
    """Generate market insights from job data"""
    insights = []
    
    # Web3 prevalence
    web3_jobs = len([job for job in jobs_list if any(keyword in job.get('description', '').lower() 
                    for keyword in ['web3', 'blockchain', 'defi', 'smart contract'])])
    
    web3_percentage = (web3_jobs / len(jobs_list) * 100) if jobs_list else 0
    insights.append(f"🌐 {web3_percentage:.1f}% of jobs are Web3-related")
    
    # Remote work prevalence
    remote_jobs = len([job for job in jobs_list if 'remote' in job.get('location', '').lower()])
    remote_percentage = (remote_jobs / len(jobs_list) * 100) if jobs_list else 0
    insights.append(f"🏠 {remote_percentage:.1f}% offer remote work")
    
    # Salary insights
    salary_jobs = [job for job in jobs_list if job.get('salary') and job['salary'] != 'Not specified']
    if salary_jobs:
        insights.append(f"💰 {len(salary_jobs)} jobs specify salary information")
    
    return insights

# Test function with real data
def test_real_matching():
    """Test the matching algorithm with realistic data"""
    
    # Load real CV content
    try:
        from config import config
        cv_text = config.get_cv_content()
    except:
        cv_text = """Lucas Rizzo - Web3 Engineer and DeFi Bot Developer
        Experience with Solidity, smart contracts, flash loans, and liquidation bots.
        Proficient in Python, JavaScript, Node.js, and React.
        Built automated ERC-20 token ecosystems and MEV protection systems.
        CompTIA Security+ certified. Achieved 18% response rate in job applications.
        Prefers remote work and async collaboration."""
    
    # Test with realistic job description
    sample_job = """Senior Web3 Engineer - DeFi Protocol Labs
    We are looking for a Senior Web3 Engineer with extensive Solidity experience.
    Must have experience with smart contracts, DeFi protocols, and flash loans.
    Python and JavaScript skills required for backend development.
    Experience with liquidation systems and MEV protection preferred.
    Remote work available. Competitive salary £80k-£120k.
    CompTIA Security+ or similar certifications preferred."""
    
    score = match_score(cv_text, sample_job)
    analysis = analyze_match(cv_text, sample_job)
    
    print(f"\n🧪 REAL MATCHING TEST RESULTS:")
    print(f"📊 Overall Match Score: {score:.3f}")
    print(f"🎯 Match Strength: {analysis['match_strength']}")
    print(f"🚀 Application Priority: {analysis['application_priority']}")
    print(f"📝 Recommendations:")
    for rec in analysis['recommendations']:
        print(f"   • {rec}")
    
    return score, analysis

if __name__ == "__main__":
    # Run test with real matching
    test_real_matching()
