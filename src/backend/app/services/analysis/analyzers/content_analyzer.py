"""
Content Analysis Module

Pure content analysis functionality that can be reused across multiple features.
Analyzes text documents to extract structural and semantic information.

Design Principles:
- Single Responsibility: Only analyzes content, doesn't make decisions about usage
- No side effects: Pure functions that return structured data
- Reusable: Can be imported by skill extractors, resume generators, etc.
- Testable: Each function can be tested independently

Usage Examples:
    # For skill extraction
    from app.services.analysis.analyzers.content_analyzer import analyze_document
    analysis = analyze_document(text, file_path)
    skills = extract_skills_from_analysis(analysis)
    
    # For resume generation
    from app.services.analysis.analyzers.content_analyzer import analyze_project_content
    content_summary = analyze_project_content(files)
    resume_items = generate_items_from_content(content_summary)
"""

from typing import Dict, Any, List
from collections import Counter
from dataclasses import dataclass
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class DocumentAnalysis:
    """
    Structured analysis result for a single document.
    Immutable data class for easy passing between modules.
    """
    # Basic metrics
    word_count: int
    character_count: int
    paragraph_count: int
    sentence_count: int
    
    # Classification
    document_type: str  # 'research_paper', 'technical_doc', 'blog_post', etc.
    writing_style: str  # 'academic', 'technical', 'casual', 'creative', 'formal'
    complexity_level: str  # 'basic', 'intermediate', 'advanced'
    
    # Content analysis
    topics: List[str]  # Main topics identified
    key_terms: List[str]  # Important terms/phrases
    domain_indicators: Dict[str, int]  # Domain-specific keyword counts
    
    # Structure indicators
    has_citations: bool
    has_code_blocks: bool
    has_mathematical_notation: bool
    has_lists: bool
    has_tables: bool
    has_headings: bool
    
    # Derived metrics
    avg_word_length: float
    avg_sentence_length: float
    estimated_read_time: int  # minutes
    
    # Raw data for advanced analysis
    vocabulary_richness: float  # Unique words / total words
    specialized_term_count: int


@dataclass
class ProjectContentSummary:
    """
    Aggregated analysis for all content files in a project.
    Provides high-level overview suitable for resume generation.
    """
    total_documents: int
    total_words: int
    total_characters: int
    
    # Document type distribution
    document_types: Dict[str, int]  # {'research_paper': 2, 'blog_post': 3}
    primary_document_type: str
    
    # Writing characteristics
    writing_styles: List[str]
    primary_writing_style: str
    complexity_levels: List[str]
    primary_complexity: str
    
    # Content themes
    all_topics: List[str]  # All topics from all documents
    primary_topics: List[str]  # Top 5 most common topics
    domain_indicators: Dict[str, int]  # Aggregated domain keyword counts
    
    # Structural features
    has_citations: bool
    has_code_examples: bool
    has_mathematical_content: bool
    
    # Aggregate metrics
    average_document_length: int
    estimated_total_read_time: int
    vocabulary_richness: float
    
    # Individual document analyses (for detailed use)
    document_analyses: List[DocumentAnalysis]


class ContentAnalyzer:
    """
    Core content analysis engine.
    Stateless class with pure analysis methods.
    """
    
    def analyze_document(self, text: str, file_path: str = "") -> DocumentAnalysis:
        """
        Analyze a single document and return structured results.
        
        This is the main entry point for document analysis. Returns a comprehensive
        DocumentAnalysis object that can be used by various consumers.
        
        Args:
            text: Document text content
            file_path: Optional file path for additional context
            
        Returns:
            DocumentAnalysis with all extracted information
        """
        if not text or not text.strip():
            return self._empty_analysis()
        
        # Basic metrics
        words = self._tokenize_words(text)
        sentences = self._split_sentences(text)
        paragraphs = self._split_paragraphs(text)
        
        # Classification
        doc_type = self._classify_document_type(text, file_path)
        style = self._detect_writing_style(text)
        complexity = self._assess_complexity(words, sentences)
        
        # Content analysis
        topics = self._extract_topics(text)
        key_terms = self._extract_key_terms(text)
        domain_indicators = self._count_domain_indicators(text)
        
        # Structure detection
        has_citations = self._detect_citations(text)
        has_code = self._detect_code_blocks(text)
        has_math = self._detect_mathematical_notation(text)
        has_lists = self._detect_lists(text)
        has_tables = self._detect_tables(text)
        has_headings = self._detect_headings(text)
        
        # Derived metrics
        avg_word_len = sum(len(w) for w in words) / len(words) if words else 0
        avg_sent_len = len(words) / len(sentences) if sentences else 0
        read_time = self._estimate_read_time(len(words))
        vocab_richness = len(set(words)) / len(words) if words else 0
        specialized_count = self._count_specialized_terms(text)
        
        return DocumentAnalysis(
            word_count=len(words),
            character_count=len(text),
            paragraph_count=len(paragraphs),
            sentence_count=len(sentences),
            document_type=doc_type,
            writing_style=style,
            complexity_level=complexity,
            topics=topics,
            key_terms=key_terms,
            domain_indicators=domain_indicators,
            has_citations=has_citations,
            has_code_blocks=has_code,
            has_mathematical_notation=has_math,
            has_lists=has_lists,
            has_tables=has_tables,
            has_headings=has_headings,
            avg_word_length=avg_word_len,
            avg_sentence_length=avg_sent_len,
            estimated_read_time=read_time,
            vocabulary_richness=vocab_richness,
            specialized_term_count=specialized_count
        )
    
    def analyze_project_content(
        self, 
        files_with_text: List[Dict[str, Any]]
    ) -> ProjectContentSummary:
        """
        Analyze all content files in a project.
        
        Args:
            files_with_text: List of dicts with 'path' and 'text' keys
            
        Returns:
            ProjectContentSummary with aggregated analysis
        """
        if not files_with_text:
            return self._empty_project_summary()
        
        # Analyze each document
        analyses = []
        for file_data in files_with_text:
            text = file_data.get('text', '')
            path = file_data.get('path', '')
            if text and text.strip():
                analysis = self.analyze_document(text, path)
                analyses.append(analysis)
        
        if not analyses:
            return self._empty_project_summary()
        
        # Aggregate results
        doc_types = Counter(a.document_type for a in analyses)
        styles = [a.writing_style for a in analyses]
        complexities = [a.complexity_level for a in analyses]
        
        all_topics = []
        for a in analyses:
            all_topics.extend(a.topics)
        topic_counts = Counter(all_topics)
        
        # Merge domain indicators
        merged_domains = Counter()
        for a in analyses:
            merged_domains.update(a.domain_indicators)
        
        return ProjectContentSummary(
            total_documents=len(analyses),
            total_words=sum(a.word_count for a in analyses),
            total_characters=sum(a.character_count for a in analyses),
            document_types=dict(doc_types),
            primary_document_type=doc_types.most_common(1)[0][0] if doc_types else 'unknown',
            writing_styles=list(set(styles)),
            primary_writing_style=Counter(styles).most_common(1)[0][0] if styles else 'formal',
            complexity_levels=list(set(complexities)),
            primary_complexity=Counter(complexities).most_common(1)[0][0] if complexities else 'intermediate',
            all_topics=all_topics,
            primary_topics=[t for t, _ in topic_counts.most_common(5)],
            domain_indicators=dict(merged_domains),
            has_citations=any(a.has_citations for a in analyses),
            has_code_examples=any(a.has_code_blocks for a in analyses),
            has_mathematical_content=any(a.has_mathematical_notation for a in analyses),
            average_document_length=sum(a.word_count for a in analyses) // len(analyses),
            estimated_total_read_time=sum(a.estimated_read_time for a in analyses),
            vocabulary_richness=sum(a.vocabulary_richness for a in analyses) / len(analyses),
            document_analyses=analyses
        )
    
    # ========== Private Helper Methods ==========
    # These are implementation details, not part of public API
    
    def _tokenize_words(self, text: str) -> List[str]:
        """Split text into words."""
        return [w for w in re.findall(r'\b\w+\b', text.lower()) if len(w) > 0]
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        return [p.strip() for p in text.split('\n\n') if p.strip()]
    
    def _classify_document_type(self, text: str, file_path: str) -> str:
        """Classify document type based on content and structure."""
        # Check file extension hints
        path_lower = file_path.lower()
        if path_lower.endswith(('.tex', '.bib')):
            return 'research_paper'
        
        # Academic patterns
        academic_patterns = [
            r'\babstract\b', r'\bintroduction\b', r'\bmethodology\b',
            r'\bresults\b', r'\bconclusion\b', r'\breferences\b',
            r'\bet al\.'
        ]
        academic_score = sum(1 for p in academic_patterns if re.search(p, text, re.IGNORECASE))
        
        # Technical documentation patterns
        tech_patterns = [
            r'```', r'`[^`]+`', r'\b(API|SDK|CLI|REST|JSON|HTTP|KEY)\b',
            r'\b(function|method|class|parameter|return)\b'
        ]
        tech_score = sum(1 for p in tech_patterns if re.search(p, text))
        
        # Blog/article patterns MAY NEED TO BE UPDATED FOR CREATIVE WRITING OVERLAP
        blog_patterns = [
            # Instructional/tutorial language
            r'\b(how to|step by step|getting started|quick start)\b',
            r'\b(tutorial|guide|walkthrough|beginner[\'s]* guide)\b',
            r'\b(tips and tricks|best practices|pro tips)\b',
            # Listicle patterns (common in blog posts)
            r'\b(top \d+|best \d+|\d+ ways|reasons why|\d+ tips)\b',
            r'\b(\d+ things|ultimate guide|complete guide)\b',
            # Conversational/engagement language
            r'\b(let me show you|I\'ll show you|check out|take a look)\b',
            r'\b(you might be wondering|you may be asking|have you ever)\b',
            # Personal experience/opinion (blogs)
            r'\b(in my experience|personally|I recently|my take on)\b',
            r'\b(I found that|I discovered|I learned|in my opinion)\b',
            # Time/timeliness (blogs are often timely)
            r'\b(this week|this month|this year|recently|nowadays|today)\b',
            r'\b(latest|updated|new release)\b',
            # Call-to-action/engagement
            r'\b(leave a comment|share this|subscribe|follow me|join us)\b',
        ]
        blog_score = sum(1 for p in blog_patterns if re.search(p, text, re.IGNORECASE))
        
        # Creative writing patterns
        creative_patterns = [
            # Story structure
            r'\b(chapter|scene|protagonist|character|prologue|epilogue)\b',
            # Dialogue patterns (common in novels and stories)
            r'\b(he said|she said|they said|he asked|she asked|I said)\b',
            r'\b(whispered|shouted|exclaimed|murmured|replied|stammered)\b',
            # Narrative patterns
            r'\b(once upon|long ago|in a land|in the beginning)\b',
            # Character actions and emotions (strong indicators of narrative fiction)
            r'\b(he walked|she walked|he looked|she looked|he felt|she felt)\b',
            r'\b(he wondered|she wondered|he thought|she thought|he realized|she realized)\b',
            # Time transitions common in creative writing
            r'\b(the next day|later that evening|years passed|moments later|suddenly)\b',
        ]
        creative_score = sum(1 for p in creative_patterns if re.search(p, text, re.IGNORECASE))
        
        # Classify based on scores
        if creative_score >= 2:
            return 'creative_writing'
        elif blog_score >= 2:
            return 'blog_post'
        elif academic_score >= 3:
            return 'research_paper'
        elif tech_score >= 3:
            return 'technical_documentation'
        else:
            return 'general_article'
    
    def _detect_writing_style(self, text: str) -> str:
        """Detect writing style."""
        if re.search(r'\b(abstract|methodology|hypothesis)\b', text, re.IGNORECASE):
            return 'academic'
        elif re.search(r'```|`[^`]+`|\bAPI\b', text):
            return 'technical'
        elif re.search(r"\b(you'll|we'll|let's|I'm)\b", text, re.IGNORECASE):
            return 'casual'
        elif re.search(r'\b(suddenly|whispered|smiled)\b', text, re.IGNORECASE):
            return 'creative'
        else:
            return 'formal'
    
    def _assess_complexity(self, words: List[str], sentences: List[str]) -> str:
        """Assess writing complexity."""
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        # Advanced vocabulary indicators
        advanced_terms = [
            'consequently', 'nevertheless', 'furthermore', 'moreover',
            'substantial', 'comprehensive', 'methodology', 'paradigm',
            'multifaceted', 'ramifications', 'necessitate', 'interdisciplinary',
            'paramount', 'sophisticated', 'paradigmatic'
        ]
        text_lower = ' '.join(words)
        advanced_count = sum(1 for term in advanced_terms if term in text_lower)
        
        complexity_score = 0
        if avg_word_length > 5.5:
            complexity_score += 1
        if avg_sentence_length > 20:
            complexity_score += 1
        if advanced_count >= 3:
            complexity_score += 1
        
        # For very short texts (< 50 words), only use advanced vocabulary if present
        if len(words) < 50:
            return 'advanced' if advanced_count >= 3 else 'basic'
        
        return 'advanced' if complexity_score >= 2 else 'intermediate' if complexity_score == 1 else 'basic'
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics using keyword matching."""
        topic_keywords = {
            'Machine Learning': ['machine learning', 'neural network', 'deep learning', 'ai model'],
            'Web Development': ['web development', 'frontend', 'backend', ' api '],
            'Data Science': ['data science', 'data analysis', 'statistics', 'analytics'],
            'Cybersecurity': ['security', 'encryption', 'authentication', 'vulnerability'],
            'Cloud Computing': ['cloud server', 'cloud services', ' aws ', 'azure', 'kubernetes', 'docker'],
            'Mobile Development': ['mobile', 'ios', 'android', 'app development'],
            'DevOps': ['devops', 'ci/cd', 'deployment', 'automation'],
            'Database Management': ['database', 'sql', 'nosql', 'postgresql', 'mongodb'],
            'UI/UX Design': [' ux ', 'user experience', 'usability', 'user interface'],
            'Software Testing': ['testing', 'unit test', 'integration test', ' qa '],
            'Life Sciences/Biology': ['genetics', 'genome', 'protein synthesis', 'dna sequence', 'evolutionary', 'organism', 'cell division', 'phylogeny'],
            'Medicine/Healthcare': ['clinical trial', 'diagnosis', 'treatment protocol', 'patient care', 'pathology'],
            'Physical Sciences': ['quantum mechanics', 'particle physics', 'thermodynamics', 'electromagnetic', 'reactivity'],
            'Psychology': ['cognitive psychology', 'psychotherapy', 'neuroscience', 'behavioral analysis', 'mental health'],
            'Economics': ['macroeconomics', 'microeconomics', 'financial markets', 'gdp', 'inflation rate', 'economic policy'],
            'Business': ['revenue', 'profit', ' q1 ', ' q2 ', ' q3 ', ' q4 ', 'quarterly report', 'annual report', 'financial projections'],
            'Literature': ['literary analysis', 'narrative structure', 'literary criticism', 'prose', 'poetry'],
            'Philosophy': ['metaphysics', 'epistemology', 'ethics', 'philosophical argument', 'philosophy of '],
            'History': ['historical analysis', 'archaeolog', 'anthropolog', 'chronological', 'historical period', 'a.d.', 'b.c.', 'b.c.e'],
            'Education': ['pedagogy', 'curriculum', 'educational theory', 'learning outcomes'],
        }
        
        text_lower = text.lower()
        detected = []
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                detected.append(topic)
        
        return detected[:5]
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key technical terms."""
        # Find capitalized terms (likely proper nouns/technical terms)
        terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        term_counts = Counter(terms)
        return [term for term, _ in term_counts.most_common(10)]
    
    def _count_domain_indicators(self, text: str) -> Dict[str, int]: # MAY NEED TO BE UPDATED FOR CREATIVE WRITING ACCURACY
        """Count occurrences of domain-specific keywords."""
        domains = {
            'technical_writing': ['documentation', 'specification', 'guide', 'manual'],
            'academic_writing': ['research', 'study', 'analysis', 'findings', 'hypothesis'],
            'creative_writing': ['chapter',
                'whispered', 'shouted', 'murmured', 'exclaimed', 'gasped',
                'wondered', 'remembered', 'realized', 'noticed', 'felt',
                'suddenly', 'meanwhile', 'later', 'yesterday', 'tonight',
                'darkness', 'shadows', 'moonlight', 'silence',
                'walked', 'turned', 'smiled', 'laughed', 'cried'
            ],
            'business_writing': ['strategy', 'proposal', 'executive', 'stakeholder'],
            'scientific_writing': ['experiment', 'methodology', 'data', 'results'],
        }
        
        text_lower = text.lower()
        counts = {}
        for domain, keywords in domains.items():
            count = sum(text_lower.count(kw) for kw in keywords)
            if count > 0:
                counts[domain] = count
        
        return counts
    
    def _detect_citations(self, text: str) -> bool:
        """Check for citation patterns."""
        patterns = [
            r'\[\d+\]',  # [1], [2], etc.
            r'\b[A-Z][a-z]+\s+\(\d{4}\)',  # Smith (2020)
            r'\([A-Z][a-z]+,?\s+\d{4}\)',  # (Smith, 2020)
            r'\bet al\.',  # et al.
            r'\bibid\b'  # ibid
        ]
        return any(re.search(p, text) for p in patterns)
    
    def _detect_code_blocks(self, text: str) -> bool:
        """Check for code blocks."""
        return bool(re.search(r'```|`[^`]+`|\n    \w+', text))
    
    def _detect_mathematical_notation(self, text: str) -> bool:
        """Check for mathematical notation."""
        patterns = [r'\$.*?\$', r'\\[a-z]+\{', r'\b(theorem|lemma|proof|equation)\b']
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)
    
    def _detect_lists(self, text: str) -> bool:
        """Check for bullet/numbered lists."""
        return bool(re.search(r'^\s*[-*•]\s+', text, re.MULTILINE) or 
                   re.search(r'^\s*\d+\.\s+', text, re.MULTILINE))
    
    def _detect_tables(self, text: str) -> bool:
        """Check for table structures."""
        return bool(re.search(r'\|.*\|.*\|', text, re.MULTILINE))
    
    def _detect_headings(self, text: str) -> bool:
        """Check for markdown/structured headings."""
        return bool(re.search(r'^\s*#+\s+', text, re.MULTILINE))
    
    def _estimate_read_time(self, word_count: int) -> int:
        """Estimate reading time (avg 200 words/min)."""
        return max(1, word_count // 200)
    
    def _count_specialized_terms(self, text: str) -> int:
        """Count specialized/technical terms (simplified heuristic)."""
        # Look for words with specific patterns that indicate technical terms
        specialized = re.findall(r'\b[A-Z]{2,}\b', text)  # Acronyms
        specialized += re.findall(r'\b[a-z]+[A-Z][a-z]+\b', text)  # camelCase
        return len(set(specialized))
    
    def _empty_analysis(self) -> DocumentAnalysis:
        """Return empty analysis for invalid input."""
        return DocumentAnalysis(
            word_count=0, character_count=0, paragraph_count=0, sentence_count=0,
            document_type='unknown', writing_style='unknown', complexity_level='basic',
            topics=[], key_terms=[], domain_indicators={},
            has_citations=False, has_code_blocks=False, has_mathematical_notation=False,
            has_lists=False, has_tables=False, has_headings=False,
            avg_word_length=0, avg_sentence_length=0, estimated_read_time=0,
            vocabulary_richness=0, specialized_term_count=0
        )
    
    def _empty_project_summary(self) -> ProjectContentSummary:
        """Return empty summary for projects with no content."""
        return ProjectContentSummary(
            total_documents=0, total_words=0, total_characters=0,
            document_types={}, primary_document_type='unknown',
            writing_styles=[], primary_writing_style='unknown',
            complexity_levels=[], primary_complexity='basic',
            all_topics=[], primary_topics=[], domain_indicators={},
            has_citations=False, has_code_examples=False, has_mathematical_content=False,
            average_document_length=0, estimated_total_read_time=0,
            vocabulary_richness=0, document_analyses=[]
        )


# ========== Convenience Functions ==========

def analyze_document(text: str, file_path: str = "") -> DocumentAnalysis:
    """
    Convenience function for analyzing a single document.
    
    Example:
        from app.services.analysis.analyzers.content_analyzer import analyze_document
        analysis = analyze_document(document_text, "essay.md")
        print(f"Document type: {analysis.document_type}")
        print(f"Topics: {analysis.topics}")
    """
    analyzer = ContentAnalyzer()
    return analyzer.analyze_document(text, file_path)


def analyze_project_content(files_with_text: List[Dict[str, Any]]) -> ProjectContentSummary:
    """
    Convenience function for analyzing multiple documents in a project.
    
    Example:
        from app.services.analysis.analyzers.content_analyzer import analyze_project_content
        files = [
            {'path': 'doc1.md', 'text': '...'},
            {'path': 'doc2.md', 'text': '...'},
        ]
        summary = analyze_project_content(files)
        print(f"Total words: {summary.total_words}")
        print(f"Primary topics: {summary.primary_topics}")
    """
    analyzer = ContentAnalyzer()
    return analyzer.analyze_project_content(files_with_text)

