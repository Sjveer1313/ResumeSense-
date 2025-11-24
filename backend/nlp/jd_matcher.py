"""
Job Description Matcher
Computes match score between resume and job description using keyword analysis.
"""
import re
from typing import Dict, List, Set
from collections import Counter


class JDMatcher:
    """Match resume against job description"""
    
    # Scientific and technical domain indicators
    SCIENTIFIC_DOMAINS = {
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'cpp', 'c#', 'csharp',
        'go', 'golang', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl',
        'ruby', 'php', 'sql', 'html', 'css', 'xml', 'json', 'yaml',
        # Frameworks & Libraries
        'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'node',
        'tensorflow', 'pytorch', 'keras', 'scikit', 'pandas', 'numpy', 'matplotlib',
        # Technologies & Tools
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github',
        'gitlab', 'ci/cd', 'microservices', 'api', 'rest', 'graphql', 'mongodb',
        'postgresql', 'mysql', 'redis', 'elasticsearch', 'kafka', 'rabbitmq',
        # Scientific Terms
        'machine learning', 'deep learning', 'neural network', 'nlp', 'computer vision',
        'data science', 'statistics', 'algorithm', 'optimization', 'regression',
        'classification', 'clustering', 'reinforcement learning', 'ai', 'artificial intelligence',
        # Technical Skills
        'linux', 'unix', 'bash', 'shell', 'agile', 'scrum', 'devops', 'cloud',
        'security', 'encryption', 'blockchain', 'cryptography', 'networking',
        # Academic/Research Terms
        'research', 'publication', 'thesis', 'dissertation', 'peer review', 'journal',
        'conference', 'patent', 'algorithm', 'methodology', 'hypothesis', 'experiment'
    }
    
    @staticmethod
    def compute_match_score(resume_text: str, jd_text: str) -> Dict:
        """
        Compute match score between resume and job description.
        
        Args:
            resume_text: Extracted resume text
            jd_text: Job description text
            
        Returns:
            Dictionary with match score and details
        """
        # Tokenize and clean both texts
        resume_tokens = JDMatcher._tokenize(resume_text)
        jd_tokens = JDMatcher._tokenize(jd_text)
        
        # Extract scientific/technical keywords (weighted more heavily)
        resume_scientific = JDMatcher._extract_scientific_keywords(resume_text)
        jd_scientific = JDMatcher._extract_scientific_keywords(jd_text)
        
        # Get general keyword sets (excluding common stop words)
        resume_keywords = JDMatcher._extract_keywords(resume_tokens)
        jd_keywords = JDMatcher._extract_keywords(jd_tokens)
        
        # Compute scientific keyword overlap (weighted 70%)
        common_scientific = resume_scientific.intersection(jd_scientific)
        total_jd_scientific = len(jd_scientific)
        
        # Compute general keyword overlap (weighted 30%)
        common_keywords = resume_keywords.intersection(jd_keywords)
        total_jd_keywords = len(jd_keywords)
        
        # Calculate weighted match score
        if total_jd_scientific == 0 and total_jd_keywords == 0:
            match_score = 0.0
        else:
            scientific_score = 0.0
            general_score = 0.0
            
            if total_jd_scientific > 0:
                scientific_score = (len(common_scientific) / total_jd_scientific) * 100
            
            if total_jd_keywords > 0:
                general_score = (len(common_keywords) / total_jd_keywords) * 100
            
            # Weight scientific keywords 70%, general keywords 30%
            match_score = (scientific_score * 0.7) + (general_score * 0.3)
        
        # Ensure score is between 0 and 100
        match_score = min(100.0, max(0.0, match_score))
        
        # Extract important keywords from JD (focus on scientific/technical)
        jd_important = JDMatcher._extract_important_keywords(jd_text)
        matched_important = [kw for kw in jd_important if kw.lower() in resume_text.lower()]
        
        # Combine scientific and general keywords for display
        all_common = list(common_scientific) + [kw for kw in common_keywords if kw not in common_scientific]
        all_missing = list(jd_scientific - resume_scientific) + [kw for kw in (jd_keywords - resume_keywords) if kw not in (jd_scientific - resume_scientific)]
        
        return {
            'match_score': round(match_score, 2),
            'common_keywords': all_common[:20],  # Top 20 (scientific keywords prioritized)
            'missing_keywords': all_missing[:20],  # Top 20 missing (scientific keywords prioritized)
            'jd_keyword_count': total_jd_keywords + total_jd_scientific,
            'resume_keyword_count': len(resume_keywords) + len(resume_scientific),
            'scientific_keywords_matched': len(common_scientific),
            'scientific_keywords_total': total_jd_scientific,
            'important_keywords_matched': len(matched_important),
            'important_keywords_total': len(jd_important),
            'matched_important_keywords': matched_important[:10]
        }
    
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        # Convert to lowercase and split
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    @staticmethod
    def _extract_scientific_keywords(text: str) -> Set[str]:
        """
        Extract scientific and technical keywords from text.
        Focuses on domain-specific terminology.
        
        Args:
            text: Input text
            
        Returns:
            Set of scientific/technical keywords
        """
        text_lower = text.lower()
        scientific_keywords = set()
        
        # Check for scientific domain terms
        for domain in JDMatcher.SCIENTIFIC_DOMAINS:
            if domain in text_lower:
                scientific_keywords.add(domain)
        
        # Find technical acronyms (2-5 uppercase letters)
        acronyms = re.findall(r'\b[A-Z]{2,5}\b', text)
        scientific_keywords.update(ac.lower() for ac in acronyms)
        
        # Find technology patterns (e.g., React.js, Node.js, etc.)
        tech_patterns = re.findall(r'\b(\w+)\.(js|py|java|cpp|html|css|sql|json|xml|ts|tsx|jsx)\b', text_lower)
        scientific_keywords.update([tech[0] for tech in tech_patterns])  # Extract the technology name
        
        # Find compound technical terms (e.g., "machine learning", "deep learning")
        compound_terms = [
            'machine learning', 'deep learning', 'neural network', 'natural language',
            'computer vision', 'data science', 'artificial intelligence', 'reinforcement learning',
            'supervised learning', 'unsupervised learning', 'transfer learning', 'feature engineering',
            'ci/cd', 'devops', 'microservices', 'rest api', 'graphql', 'object oriented',
            'functional programming', 'test driven', 'agile methodology', 'scrum master'
        ]
        
        for term in compound_terms:
            if term in text_lower:
                scientific_keywords.add(term.replace(' ', '_'))  # Use underscore for multi-word
        
        return scientific_keywords
    
    @staticmethod
    def _extract_keywords(tokens: List[str]) -> Set[str]:
        """
        Extract meaningful keywords, excluding common stop words.
        Focuses on non-scientific but relevant terms.
        
        Args:
            tokens: List of tokenized words
            
        Returns:
            Set of keywords
        """
        # Common stop words to exclude
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
            'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now',
            'work', 'job', 'position', 'role', 'team', 'company', 'years', 'experience',
            'responsible', 'responsibilities', 'requirement', 'requirements',
            'preferred', 'including', 'include', 'ensure', 'ensuring', 'across',
            'within', 'using', 'leveraging', 'strong', 'excellent', 'communication',
            'collaboration', 'collaborative', 'stakeholder', 'stakeholders',
            'deliver', 'delivery', 'provide', 'ability', 'candidate', 'looking',
            'seeking', 'fast', 'paced', 'environment', 'detail', 'detailed',
            'driven', 'passion', 'passionate', 'motivated',
            'self', 'starter', 'dynamic', 'highly', 'plus'
        }
        
        # Filter out stop words, short words, and scientific terms (already counted separately)
        keywords = {token for token in tokens 
                   if token not in stop_words 
                   and len(token) > 2
                   and token not in JDMatcher.SCIENTIFIC_DOMAINS}
        return keywords
    
    @staticmethod
    def _extract_important_keywords(jd_text: str) -> List[str]:
        """
        Extract important keywords from job description.
        Prioritizes scientific and technical terms.
        
        Args:
            jd_text: Job description text
            
        Returns:
            List of important keywords (scientific/technical prioritized)
        """
        important = []
        
        # First, extract scientific keywords (highest priority)
        scientific = JDMatcher._extract_scientific_keywords(jd_text)
        important.extend([kw.replace('_', ' ').title() if '_' in kw else kw.title() 
                          for kw in scientific])
        
        # Find capitalized words (likely technologies, tools, or important terms)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', jd_text)
        
        # Find technical file extensions and patterns
        technical_patterns = [
            r'\b\w+\.(js|py|java|cpp|html|css|sql|json|xml|ts|tsx|jsx)\b',
            r'\b[A-Z]{2,5}\b',  # Acronyms (2-5 letters)
        ]
        
        technical_terms = []
        for pattern in technical_patterns:
            technical_terms.extend(re.findall(pattern, jd_text, re.IGNORECASE))
        
        # Add capitalized and technical terms
        important.extend(capitalized)
        important.extend(technical_terms)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_important = []
        for kw in important:
            kw_lower = kw.lower()
            if kw_lower not in seen and kw_lower not in {'the', 'this', 'we', 'you', 'your', 'our', 'company', 'team'}:
                seen.add(kw_lower)
                unique_important.append(kw)
        
        return unique_important[:30]  # Top 30 important keywords

