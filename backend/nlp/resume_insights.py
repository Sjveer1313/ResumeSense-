"""
Resume insights helper.
Extracts project and achievement/co-curricular highlights from resume text.
"""
import re
from typing import Dict, List, Set


class ResumeInsights:
    """Extract structured information (projects, achievements) from resume text."""

    PROJECT_KEYWORDS = {
        'project', 'projects', 'capstone', 'portfolio', 'application', 'app',
        'tool', 'platform', 'system', 'product', 'prototype', 'solution',
        'hackathon', 'case study', 'research project', 'module', 'feature'
    }

    ACHIEVEMENT_KEYWORDS = {
        'award', 'awarded', 'honor', 'honours', 'recognition', 'recognized',
        'certification', 'certified', 'achievement', 'achievements',
        'winner', 'won', 'finalist', 'runner-up', 'placed', 'scholarship',
        'publication', 'published', 'speaker', 'presented', 'selected'
    }

    CO_CURRICULAR_KEYWORDS = {
        'club', 'society', 'association', 'organization', 'organised',
        'organized', 'volunteer', 'volunteered', 'leadership', 'captain',
        'coach', 'mentor', 'event', 'festival', 'competition', 'contest',
        'sports', 'athletics', 'cultural', 'music', 'dance', 'drama',
        'community', 'campus', 'co-curricular', 'extracurricular'
    }

    TECH_TERMS: Set[str] = {
        # Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'cpp', 'c#',
        'csharp', 'go', 'golang', 'rust', 'swift', 'kotlin', 'scala',
        'ruby', 'php', 'r', 'matlab', 'sql', 'nosql', 'html', 'css',
        # Frameworks
        'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express',
        'node', 'nodejs', 'fastapi', 'nextjs', 'nuxt', 'laravel', 'rails',
        # Data / ML
        'pandas', 'numpy', 'scikit-learn', 'sklearn', 'tensorflow',
        'pytorch', 'keras', 'matplotlib', 'seaborn', 'spark', 'hadoop',
        'airflow', 'dbt',
        # Cloud / DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'helm', 'terraform',
        'ansible', 'jenkins', 'gitlab', 'github', 'bitbucket', 'ci/cd',
        # Databases
        'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'dynamodb',
        'snowflake', 'bigquery', 'redshift', 'elastic', 'elasticsearch'
    }

    @staticmethod
    def extract_insights(resume_text: str) -> Dict[str, List[Dict]]:
        """
        Extract projects and achievements/co-curricular activities.

        Args:
            resume_text: Full resume text.

        Returns:
            Dictionary with projects and achievements lists.
        """
        sentences = ResumeInsights._split_sentences(resume_text)
        projects = ResumeInsights._extract_projects(sentences)
        achievements = ResumeInsights._extract_achievements(sentences)

        return {
            'projects': projects[:5],
            'achievements': achievements[:5]
        }

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """Split resume text into sentences/clauses while keeping bullets."""
        # Replace bullet characters with periods for easier splitting
        normalized = re.sub(r'[•▪●◦]', '. ', text)
        normalized = re.sub(r'\s+', ' ', normalized)
        parts = re.split(r'(?<=[\.\!\?])\s+', normalized)
        return [part.strip() for part in parts if len(part.strip()) > 25]

    @staticmethod
    def _extract_projects(sentences: List[str]) -> List[Dict]:
        projects = []
        seen_titles = set()

        for sentence in sentences:
            lower = sentence.lower()
            indicator_hits = sum(1 for kw in ResumeInsights.PROJECT_KEYWORDS if kw in lower)
            if indicator_hits == 0:
                continue

            tech_stack = ResumeInsights._extract_tech_stack(lower)
            title = ResumeInsights._infer_project_title(sentence)
            if title.lower() in seen_titles:
                continue

            confidence = min(1.0, 0.3 * indicator_hits + (0.2 if tech_stack else 0) + min(len(sentence) / 250, 0.5))
            projects.append({
                'title': title,
                'summary': sentence.strip(),
                'tech_stack': tech_stack,
                'confidence': round(confidence, 2)
            })
            seen_titles.add(title.lower())

        projects.sort(key=lambda item: item['confidence'], reverse=True)
        return projects

    @staticmethod
    def _extract_achievements(sentences: List[str]) -> List[Dict]:
        achievements = []
        seen = set()

        for sentence in sentences:
            lower = sentence.lower()
            achievement_hits = sum(1 for kw in ResumeInsights.ACHIEVEMENT_KEYWORDS if kw in lower)
            co_curricular_hit = any(kw in lower for kw in ResumeInsights.CO_CURRICULAR_KEYWORDS)

            if achievement_hits == 0 and not co_curricular_hit:
                continue

            title = ResumeInsights._infer_achievement_title(sentence)
            if title.lower() in seen:
                continue

            category = 'Co-curricular' if co_curricular_hit else 'Achievement'
            impact_keywords = ResumeInsights._extract_impact_keywords(lower)

            achievements.append({
                'title': title,
                'details': sentence.strip(),
                'category': category,
                'impact_keywords': impact_keywords
            })
            seen.add(title.lower())

        return achievements

    @staticmethod
    def _extract_tech_stack(text_lower: str) -> List[str]:
        stack = []
        for term in ResumeInsights.TECH_TERMS:
            if term in text_lower:
                stack.append(term.upper() if term.isalpha() and len(term) <= 4 else term.title())
        return stack[:8]

    @staticmethod
    def _infer_project_title(sentence: str) -> str:
        match = re.search(r'(?:project|application|platform|system)\s*[:\-]\s*([A-Za-z0-9 ,&()\/\-]+)', sentence, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            return ResumeInsights._trim_title(candidate)

        # Use first clause as fallback
        clause = sentence.split(',')[0]
        clause = clause.split(' - ')[0]
        clause = clause.split('. ')[0]
        return ResumeInsights._trim_title(clause)

    @staticmethod
    def _infer_achievement_title(sentence: str) -> str:
        match = re.search(r'(?:awarded|won|received|recognized for)\s+([A-Za-z0-9 ,&()\/\-]+)', sentence, re.IGNORECASE)
        if match:
            return ResumeInsights._trim_title(match.group(1))

        clause = sentence.split('. ')[0]
        return ResumeInsights._trim_title(clause)

    @staticmethod
    def _trim_title(text: str) -> str:
        cleaned = re.sub(r'[^A-Za-z0-9 ,&()\/\-]', '', text).strip()
        if not cleaned:
            return "Highlighted Project"
        words = cleaned.split()
        return ' '.join(words[:10])

    @staticmethod
    def _extract_impact_keywords(text_lower: str) -> List[str]:
        impact_terms = [
            'led', 'organized', 'increased', 'reduced', 'boosted',
            'improved', 'mentored', 'trained', 'volunteered',
            'collaborated', 'presented', 'coordinated', 'hosted'
        ]
        hits = [term for term in impact_terms if term in text_lower]
        return hits[:5]

