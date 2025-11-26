"""
Resume Item Generator Service

This module generates professional resume bullet points for projects based on
detected skills, languages, frameworks, project classification, and git contribution
statistics. The service is modular and can be used from any endpoint.

Main function:
    - generate_resume_items(): Generate resume bullet points for a project
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ResumeItemGenerator:
    """
    Service for generating professional resume bullet points from project data.
    
    This service uses templates to create resume-ready bullet points that can be
    copied directly into a resume. Templates are organized by project type and
    collaboration status.
    
    Future enhancements:
    - User customization: Allow users to select which templates to use
    - Template editing: Allow users to modify template text
    - Multiple output formats: Support different resume styles (ATS-friendly, creative, etc.)
    - Skill-based filtering: Generate items focused on specific skills
    - Length customization: Allow users to request more/fewer items
    - Git contribution filtering: Allow users to filter by contribution percentage thresholds
    - File-specific tracking: Track which specific files a user edited and include
      file-level details in resume items (e.g., "Developed core API endpoints across
      15 Python files" or "Implemented authentication system in auth.py and middleware.py")
    """
    
    def __init__(self):
        """Initialize the resume item generator with templates."""
        self.templates = self._initialize_templates()
    
    def generate_resume_items(
        self, 
        project_data: Dict[str, Any], 
        user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate resume bullet points for a project.
        
        Args:
            project_data: Project data dictionary containing:
                - root: Project root folder name
                - classification: Dict with type, languages, frameworks, resume_skills
                - created_at: Start date timestamp (optional)
                - end_date: End date timestamp (optional)
                - contributors: List of contributor dicts (optional)
                - collaborative: Boolean indicating if collaborative (optional)
                - files: Dict with file counts (optional)
            user_name: Optional username to extract user-specific contribution stats
            
        Returns:
            Dict with:
                - items: List of resume bullet point strings
                - generated_at: Timestamp when items were generated
        """
        try:
            # Extract project metadata
            project_name = project_data.get('root', 'Project')
            classification = project_data.get('classification') or {}
            project_type = classification.get('type', 'unknown') if isinstance(classification, dict) else 'unknown'
            
            # Extract dates
            start_date_ts = project_data.get('created_at')
            end_date_ts = project_data.get('end_date')
            start_date = self._format_date(start_date_ts) if start_date_ts else ''
            end_date = self._format_date(end_date_ts) if end_date_ts else ''
            date_range = self._format_date_range(start_date_ts, end_date_ts)
            
            # Extract technical data
            languages = classification.get('languages', []) if isinstance(classification, dict) else []
            frameworks = classification.get('frameworks', []) if isinstance(classification, dict) else []
            skills = classification.get('resume_skills', []) if isinstance(classification, dict) else []
            primary_language = languages[0] if languages else ''
            
            # Extract file counts
            files = project_data.get('files', {})
            file_count = (
                len(files.get('code', [])) +
                len(files.get('content', [])) +
                len(files.get('image', [])) +
                len(files.get('unknown', []))
            )
            code_files = len(files.get('code', []))
            
            # Extract git contribution data
            contributors = project_data.get('contributors', [])
            is_collaborative = project_data.get('collaborative', False)
            contributor_count = len([c for c in contributors if c.get('commits', 0) > 0])
            
            # Extract user-specific or aggregate git stats
            git_stats = self._extract_user_contributions(contributors, user_name)
            has_git_stats = bool(git_stats.get('total_commits') or git_stats.get('user_commits'))
            has_user_stats = 'user_commits' in git_stats  # Check if user-specific stats are available
            
            # Build template context
            # For contextual templates, we need ALL frameworks/languages, not just top 3
            all_frameworks_str = ', '.join(frameworks) if frameworks else ''
            all_languages_str = ', '.join(languages) if languages else ''
            
            context = {
                'project_name': project_name,
                'start_date': start_date,
                'end_date': end_date,
                'date_range': date_range,
                'primary_language': primary_language,
                'languages': ', '.join(languages[:3]) if languages else '',  # Top 3 languages for display
                'frameworks': ', '.join(frameworks[:3]) if frameworks else '',  # Top 3 frameworks for display
                'all_frameworks': all_frameworks_str,  # ALL frameworks for contextual template matching
                'all_languages': all_languages_str,  # ALL languages for contextual template matching
                'skills': ', '.join(skills[:5]) if skills else '',  # Top 5 skills
                'file_count': file_count,
                'code_files': code_files,
                'is_collaborative': is_collaborative,
                'contributor_count': contributor_count,
                **git_stats  # Merge git stats into context
            }
            
            # Step 1: Gather all contextual templates and track what they cover
            contextual_items, covered_items = self._gather_contextual_items(context, frameworks, languages, skills)
            
            # Step 2: Generate generic templates that avoid covered concepts
            # If we have < 5 contextual items, generate 2 generic; if >= 5, generate 1 generic
            generic_count = 2 if len(contextual_items) < 5 else 1
            template_set = self._get_template_set(project_type, is_collaborative, has_git_stats, has_user_stats)
            generic_items = self._generate_generic_items(
                template_set, context, covered_items, generic_count, 
                frameworks, languages, skills
            )
            
            # Combine contextual and generic items
            items = contextual_items + generic_items
            
            # Determine if project has limited information (few skills/languages/frameworks)
            has_limited_info = (
                len(frameworks) < 2 or 
                len(languages) < 2 or 
                len(skills) < 3 or
                (len(frameworks) + len(languages) + len(skills)) < 5
            )
            
            # Set minimum based on available information
            min_items = 4 if has_limited_info else 3
            
            # Ensure we have at least the minimum number of items
            if len(items) < min_items:
                # Add generic fallback templates
                fallback_items = self._get_fallback_templates(project_type, context)
                items.extend(fallback_items[:min_items - len(items)])
            
            # Limit to 6 items (target)
            items = items[:6]
            
            return {
                'items': items,
                'generated_at': int(datetime.now().timestamp())
            }
            
        except Exception as e:
            logger.error(f"Error generating resume items: {e}", exc_info=True)
            return {
                'items': [],
                'generated_at': int(datetime.now().timestamp())
            }
    
    def _extract_user_contributions(
        self, 
        contributors: List[Dict], 
        user_name: Optional[str]
    ) -> Dict[str, Any]:
        """
        Extract user-specific git contribution statistics.
        
        Args:
            contributors: List of contributor dictionaries
            user_name: Optional username to match against contributors
            
        Returns:
            Dict with git statistics (user-specific if user_name provided, else aggregate)
        """
        if not contributors:
            return {}
        
        # Calculate aggregate stats
        total_commits = sum(c.get('commits', 0) for c in contributors)
        
        # If user_name provided, try to find user's contributions
        if user_name:
            user_name_lower = user_name.lower()
            
            def _matches(u: str, c: dict) -> bool:
                """Match user name to contributor (similar to data_transformer logic)."""
                name = c.get('name', '').lower()
                email = c.get('email', '').lower()
                email_local = email.split('@')[0] if '@' in email else ''
                first_token = name.split()[0] if name else ''
                
                return (
                    u == name
                    or u == first_token
                    or (email_local and u == email_local)
                )
            
            # Find matching contributors
            user_contributors = [c for c in contributors if _matches(user_name_lower, c)]
            
            if user_contributors:
                # Sum up all matching contributions
                user_commits = sum(c.get('commits', 0) for c in user_contributors)
                user_lines_added = sum(c.get('lines_added', 0) for c in user_contributors)
                user_lines_deleted = sum(c.get('lines_deleted', 0) for c in user_contributors)
                user_commit_percent = round((user_commits / total_commits * 100) if total_commits > 0 else 0, 1)
                
                return {
                    'total_commits': total_commits,
                    'user_commits': user_commits,
                    'user_commit_percent': user_commit_percent,
                    'user_lines_added': user_lines_added,
                    'user_lines_deleted': user_lines_deleted,
                }
        
        # Return aggregate stats if no user match
        return {
            'total_commits': total_commits,
            'contributor_count': len([c for c in contributors if c.get('commits', 0) > 0])
        }
    
    def _extract_covered_items_from_text(self, text: str, frameworks: List[str], languages: List[str], skills: List[str]) -> Dict[str, List[str]]:
        """
        Extract which frameworks, languages, and skills are mentioned in formatted text.
        
        Args:
            text: Formatted resume item text
            frameworks: List of all frameworks in the project
            languages: List of all languages in the project
            skills: List of all skills in the project
            
        Returns:
            Dict with 'frameworks', 'languages', 'skills' lists of items found in text
        """
        text_lower = text.lower()
        covered = {
            'frameworks': [],
            'languages': [],
            'skills': []
        }
        
        # Check for frameworks (case-insensitive substring match)
        for fw in frameworks:
            if fw.lower() in text_lower:
                covered['frameworks'].append(fw)
        
        # Check for languages (case-insensitive substring match)
        for lang in languages:
            if lang.lower() in text_lower:
                covered['languages'].append(lang)
        
        # Check for skills (case-insensitive substring match)
        for skill in skills:
            if skill.lower() in text_lower:
                covered['skills'].append(skill)
        
        return covered
    
    def _gather_contextual_items(
        self, 
        context: Dict, 
        frameworks: List[str], 
        languages: List[str], 
        skills: List[str]
    ) -> tuple[List[str], Dict[str, List[str]]]:
        """
        Gather all contextual templates and track which frameworks/languages/skills they cover.
        
        Args:
            context: Template context with project data
            frameworks: List of all frameworks in the project
            languages: List of all languages in the project
            skills: List of all skills in the project
            
        Returns:
            Tuple of (list of contextual items, dict of covered items)
        """
        contextual_templates = self._get_contextual_templates(context)
        contextual_items = []
        covered_items = {
            'frameworks': [],
            'languages': [],
            'skills': []
        }
        
        for template in contextual_templates:
            try:
                item = template.format(**context)
                # Only add if template was successfully filled (no empty placeholders)
                if item and '{' not in item:
                    contextual_items.append(item)
                    # Extract what frameworks/languages/skills this item covers
                    covered = self._extract_covered_items_from_text(item, frameworks, languages, skills)
                    # Add to covered items (avoid duplicates)
                    for key in ['frameworks', 'languages', 'skills']:
                        for item_name in covered[key]:
                            if item_name not in covered_items[key]:
                                covered_items[key].append(item_name)
            except (KeyError, Exception) as e:
                # Skip templates with missing variables or formatting errors
                logger.debug(f"Skipping contextual template due to error: {e}")
                continue
        
        return contextual_items, covered_items
    
    def _generate_generic_items(
        self,
        template_set: List[str],
        context: Dict,
        covered_items: Dict[str, List[str]],
        count: int,
        frameworks: List[str],
        languages: List[str],
        skills: List[str]
    ) -> List[str]:
        """
        Generate generic templates that avoid mentioning covered frameworks/languages/skills.
        Also avoids repeating metrics/concepts among themselves.
        
        Args:
            template_set: Base template set for the project type
            context: Template context with project data
            covered_items: Dict of frameworks/languages/skills already covered by contextual items
            count: Number of generic items to generate
            frameworks: List of all frameworks in the project
            languages: List of all languages in the project
            skills: List of all skills in the project
            
        Returns:
            List of generic resume items
        """
        generic_items = []
        used_concepts = set()
        used_metrics = set()
        
        # Create a set of all covered items for quick lookup
        all_covered = set()
        for key in ['frameworks', 'languages', 'skills']:
            all_covered.update(item.lower() for item in covered_items[key])
        
        for template in template_set:
            if len(generic_items) >= count:
                break
                
            try:
                item = template.format(**context)
                # Only add if template was successfully filled (no empty placeholders)
                if item and '{' not in item:
                    # Check if the formatted text mentions any covered frameworks/languages/skills
                    item_lower = item.lower()
                    mentions_covered = any(covered_item in item_lower for covered_item in all_covered)
                    
                    if mentions_covered:
                        continue  # Skip templates that mention covered items
                    
                    # Extract metrics and concepts
                    item_metrics = self._extract_metrics_mentioned(item, context)
                    item_concepts = self._extract_concepts(item)
                    
                    # Check for concept overlap with other generic items
                    has_overlap = self._has_concept_overlap(item, used_concepts)
                    has_metric_repeat = self._has_metric_repetition(item_metrics, used_metrics)
                    
                    # Skip if it has overlap or metric repetition
                    if has_overlap or has_metric_repeat:
                        continue
                    
                    # Prefer items that don't mention dates, file counts, or other metrics
                    # (minimize these to focus on project quality/meat)
                    mentions_file_count = 'file_count_value' in item_metrics or 'file' in item_lower
                    mentions_date = 'date_mentioned' in item_metrics or any(month in item for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
                    mentions_commits = 'commit_count_value' in item_metrics or 'commit' in item_lower
                    
                    # Prefer items without metrics, but allow them if we need more items to reach count
                    if mentions_file_count or mentions_date or mentions_commits:
                        # Only skip if we already have enough items without metrics
                        # This allows metrics if we're struggling to find items
                        if len(generic_items) >= count - 1:
                            continue
                    
                    # Add the item
                    generic_items.append(item)
                    used_concepts.update(item_concepts)
                    used_metrics.update(item_metrics)
                    
            except (KeyError, Exception) as e:
                # Skip templates with missing variables or formatting errors
                logger.debug(f"Skipping generic template due to error: {e}")
                continue
        
        return generic_items
    
    def _get_template_set(
        self, 
        project_type: str, 
        is_collaborative: bool, 
        has_git_stats: bool,
        has_user_stats: bool = False
    ) -> List[str]:
        """
        Select appropriate templates based on project characteristics.
        
        Args:
            project_type: Project classification type (coding, writing, art, mixed, unknown)
            is_collaborative: Whether project has multiple contributors
            has_git_stats: Whether git statistics are available
            has_user_stats: Whether user-specific git statistics are available
            
        Returns:
            List of template strings to use
        """
        # Handle mixed types
        if 'mixed:' in project_type:
            # Split mixed type and get templates from each component
            components = project_type.replace('mixed:', '').split('+')
            templates = []
            for comp in components:
                comp_templates = self._get_templates_for_type(comp.strip(), is_collaborative, has_git_stats, has_user_stats)
                templates.extend(comp_templates)
            return templates[:5]  # Limit to 5 total
        
        return self._get_templates_for_type(project_type, is_collaborative, has_git_stats, has_user_stats)
    
    def _get_templates_for_type(
        self, 
        project_type: str, 
        is_collaborative: bool, 
        has_git_stats: bool,
        has_user_stats: bool = False
    ) -> List[str]:
        """Get templates for a specific project type."""
        templates = []
        
        if project_type == 'coding':
            if is_collaborative and has_git_stats and has_user_stats:
                # Collaborative coding project with user-specific git stats
                templates = self.templates['coding_collaborative'].copy()
            elif has_git_stats:
                # Solo coding project with git stats (or collaborative without user stats)
                templates = self.templates['coding_solo_stats'].copy()
            else:
                # Coding project without git stats
                templates = self.templates['coding_generic'].copy()
        elif project_type == 'writing':
            templates = self.templates['writing'].copy()
        elif project_type == 'art':
            templates = self.templates['art'].copy()
        else:
            # Unknown or other types
            templates = self.templates['generic'].copy()
        
        return templates
    
    def _add_contextual_templates(self, templates: List[str], context: Dict) -> List[str]:
        """
        Add contextual templates based on project specifics and prioritize them.
        
        Args:
            templates: Base templates for project type
            context: Template context with project data
            
        Returns:
            Combined list of templates with contextual ones prioritized first
        """
        import random
        
        # Get contextual templates
        contextual = self._get_contextual_templates(context)
        
        # Prioritize contextual templates by putting them FIRST
        # This ensures they're tried before generic templates
        all_templates = contextual + templates
        
        # Shuffle contextual templates among themselves for variety
        # But keep them before generic templates
        if contextual:
            project_seed = hash(context.get('project_name', 'default'))
            random.seed(project_seed)
            random.shuffle(contextual)
            # Shuffle base templates separately
            random.shuffle(templates)
            # Recombine: contextual first, then base
            all_templates = contextual + templates
        else:
            # No contextual templates, just shuffle base templates
            project_seed = hash(context.get('project_name', 'default'))
            random.seed(project_seed)
            random.shuffle(templates)
            all_templates = templates
        
        return all_templates
    
    def _get_fallback_templates(self, project_type: str, context: Dict) -> List[str]:
        """Get generic fallback templates when primary templates fail."""
        date_range = context.get('date_range', '')
        
        fallbacks = [
            "Worked on application development" + (f" from {date_range}" if date_range else ""),
            "Contributed to software development",
            "Participated in project implementation"
        ]
        
        return fallbacks
    
    def _extract_concepts(self, text: str) -> set:
        """
        Extract key concepts from a resume item to track what's been mentioned.
        
        Args:
            text: Resume bullet point text
            
        Returns:
            Set of concept keywords found in the text
        """
        text_lower = text.lower()
        concepts = set()
        
        # Define concept keywords to track
        concept_keywords = {
            'oop': ['object-oriented', 'object oriented', 'oop'],
            'api': ['api', 'restful', 'rest api', 'endpoint'],
            'database': ['database', 'sql', 'postgresql', 'mysql', 'mongodb'],
            'frontend': ['frontend', 'front-end', 'ui', 'user interface'],
            'backend': ['backend', 'back-end', 'server-side'],
            'testing': ['test', 'testing', 'unit test', 'tdd'],
            'deployment': ['deploy', 'deployment', 'ci/cd', 'devops'],
            'architecture': ['architect', 'architecture', 'design pattern'],
            'security': ['security', 'authentication', 'authorization'],
            'performance': ['performance', 'optimization', 'scalable', 'efficient'],
            'collaboration': ['team', 'collaborat', 'coordinat'],
            'leadership': ['led', 'lead', 'manag', 'direct'],
            'documentation': ['document', 'technical writing'],
            'algorithms': ['algorithm', 'data structure'],
            'web': ['web', 'http', 'browser'],
            'mobile': ['mobile', 'ios', 'android'],
            'cloud': ['cloud', 'aws', 'azure', 'gcp'],
            'containerization': ['docker', 'kubernetes', 'container'],
            'version_control': ['git', 'version control', 'commit history', 'branching'],
            'agile': ['agile', 'scrum', 'sprint'],
            'file_count': ['files', 'codebase', 'file count'],
            'commit_count': ['commits', 'commit'],
            'language_proficiency': ['proficiency', 'expertise', 'demonstrating', 'showcasing'],
            'date_range': ['across', 'throughout', 'during'],
            'independence': ['independently', 'solo', 'alone'],
            'establishment': ['established', 'created', 'built', 'developed', 'crafted', 'delivered'],
            'emphasis': ['emphasis on', 'focus on', 'focusing on'],
            # Machine Learning & Data Science concepts
            'machine_learning': ['machine learning', 'ml model', 'predictive model', 'training', 'tensorflow', 'pytorch', 'scikit-learn'],
            'deep_learning': ['deep learning', 'neural network', 'deep neural', 'cnn', 'rnn', 'transformer'],
            'data_science': ['data science', 'data analysis', 'data manipulation', 'pandas', 'numpy'],
            'data_visualization': ['data visualization', 'matplotlib', 'seaborn', 'visualization'],
            # Writing & Documentation concepts
            'research': ['research', 'empirical', 'literature review', 'scholarly'],
            'academic': ['academic', 'manuscript', 'peer-reviewed', 'paper'],
            'technical_docs': ['api documentation', 'technical specification', 'user guide', 'sdk'],
            'editorial': ['edited', 'copyedit', 'editorial', 'revised', 'content strategy'],
            'methodology': ['methodology', 'analysis', 'statistical', 'findings'],
            # Art & Design concepts
            'graphic_design': ['graphic design', 'branding', 'visual identity', 'logo'],
            'photo_editing': ['retouching', 'photo editing', 'color correction', 'compositing'],
            'illustration': ['illustration', 'digital art', 'concept art', 'painting'],
            'typography': ['typography', 'layout', 'composition'],
            '3d': ['3d model', 'render', 'visualization', 'animation'],
            'visual_design': ['visual design', 'aesthetic', 'cohesive'],
            'ui_ux': ['user experience', 'ux', 'prototyp', 'wireframe'],
        }
        
        for concept, keywords in concept_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                concepts.add(concept)
        
        return concepts
    
    def _has_concept_overlap(self, text: str, used_concepts: set) -> bool:
        """
        Check if a resume item overlaps too much with already used concepts.
        
        Args:
            text: Resume bullet point text to check
            used_concepts: Set of already used concepts
            
        Returns:
            True if too much overlap, False otherwise
        """
        new_concepts = self._extract_concepts(text)
        
        if not new_concepts:
            return False
        
        # Calculate overlap
        overlap = new_concepts.intersection(used_concepts)
        
        # Stricter rules for common overlaps
        # If this item has file_count + language_proficiency and we've already used those, reject
        problematic_combos = [
            {'file_count', 'language_proficiency'},
            {'commit_count', 'date_range'},
            {'establishment', 'file_count'},
            {'establishment', 'commit_count'},
            {'language_proficiency', 'establishment'},
        ]
        
        for combo in problematic_combos:
            if combo.issubset(new_concepts) and combo.issubset(used_concepts):
                return True
        
        # Calculate overlap percentage
        overlap_ratio = len(overlap) / len(new_concepts) if new_concepts else 0
        
        # More strict threshold: reject if more than 40% overlap
        return overlap_ratio > 0.4
    
    def _extract_metrics_mentioned(self, text: str, context: Dict) -> set:
        """
        Extract which specific metrics/data points are mentioned in the text.
        
        Args:
            text: Resume bullet point text
            context: Template context with actual values
            
        Returns:
            Set of metrics mentioned (e.g., 'file_count', 'commits', 'language_name')
        """
        metrics = set()
        text_lower = text.lower()
        
        # Check for specific numeric values from context
        code_files = context.get('code_files', 0)
        total_commits = context.get('total_commits', 0)
        primary_language = context.get('primary_language', '').lower()
        
        # Check if file count is mentioned
        if code_files > 0 and (str(code_files) in text or 'file' in text_lower):
            metrics.add('file_count_value')
        
        # Check if commit count is mentioned
        if total_commits > 0 and (str(total_commits) in text or 'commit' in text_lower):
            metrics.add('commit_count_value')
        
        # Check if specific language is mentioned by name
        if primary_language and primary_language in text_lower:
            metrics.add(f'language_{primary_language}')
        
        # Check if date range is mentioned
        date_range = context.get('date_range', '')
        if date_range and any(month in text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
            metrics.add('date_mentioned')
        
        # Check for common phrases
        phrase_patterns = {
            'proficiency_showcase': ['proficiency', 'expertise', 'demonstrating'],
            'comprehensive_phrase': ['comprehensive'],
            'maintained_phrase': ['maintained'],
            'established_phrase': ['established'],
            'crafted_phrase': ['crafted'],
            'delivered_phrase': ['delivered'],
            'built_independently': ['independently', 'built'],
        }
        
        for metric, patterns in phrase_patterns.items():
            if all(pattern in text_lower for pattern in patterns):
                metrics.add(metric)
        
        return metrics
    
    def _has_metric_repetition(self, new_metrics: set, used_metrics: set) -> bool:
        """
        Check if metrics are being repeated too much.
        
        Args:
            new_metrics: Metrics in the new item
            used_metrics: Metrics already used
            
        Returns:
            True if too much repetition, False otherwise
        """
        if not new_metrics:
            return False
        
        # If we're mentioning file_count + language name again, reject
        if 'file_count_value' in new_metrics and 'file_count_value' in used_metrics:
            # Check if also mentioning language
            lang_metrics_new = {m for m in new_metrics if m.startswith('language_')}
            lang_metrics_used = {m for m in used_metrics if m.startswith('language_')}
            if lang_metrics_new and lang_metrics_used:
                return True
        
        # If we're mentioning commits + date again, reject
        if 'commit_count_value' in new_metrics and 'commit_count_value' in used_metrics:
            if 'date_mentioned' in new_metrics and 'date_mentioned' in used_metrics:
                return True
        
        # Don't repeat the same action phrases too much
        action_metrics = {m for m in new_metrics if m.endswith('_phrase')}
        used_actions = {m for m in used_metrics if m.endswith('_phrase')}
        if action_metrics and action_metrics.issubset(used_actions):
            return True
        
        return False
    
    def _format_date(self, timestamp: Optional[int]) -> str:
        """
        Format Unix timestamp to "MMM YYYY" format.
        
        Args:
            timestamp: Unix timestamp (integer) or None
            
        Returns:
            Formatted date string or empty string if timestamp is None/0
        """
        if not timestamp or timestamp == 0:
            return ''
        
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime('%b %Y')
        except (ValueError, OSError, OverflowError):
            return ''
    
    def _format_date_range(
        self, 
        start: Optional[int], 
        end: Optional[int]
    ) -> str:
        """
        Format date range from start and end timestamps.
        
        Args:
            start: Start date Unix timestamp or None
            end: End date Unix timestamp or None
            
        Returns:
            Formatted date range string (e.g., "Jan 2023 - Dec 2024") or empty string
        """
        start_str = self._format_date(start)
        end_str = self._format_date(end)
        
        if start_str and end_str:
            if start_str == end_str:
                return start_str
            return f"{start_str} - {end_str}"
        elif start_str:
            return f"{start_str} - Present"
        elif end_str:
            return f"Until {end_str}"
        else:
            return ''
    
    def _initialize_templates(self) -> Dict[str, List[str]]:
        """
        Initialize template sets for different project types.
        
        Returns:
            Dictionary mapping template set names to lists of template strings
        """
        return {
            'coding_collaborative': [
                # Leadership and contribution focus
                "Led development with {user_commit_percent}% of commits, contributing {user_lines_added:,} lines of code",
                "Spearheaded architecture using {primary_language} and {frameworks}, coordinating with {contributor_count} team members",
                "Drove technical implementation, delivering {user_commits} commits and mentoring team members",
                "Architected application using {primary_language} and {frameworks}, coordinating with {contributor_count} team members",
                "Implemented {skills}, delivering {user_commits} commits across {date_range}",
                "Built scalable solution using {languages} and {frameworks}, leading a team of {contributor_count} developers",
                "Developed application with focus on {skills}, contributing {user_lines_added:,} lines of code and {user_commits} commits",
                "Orchestrated collaborative development, contributing {user_commit_percent}% of total codebase",
                "Guided team through implementation, personally delivering {user_lines_added:,} lines across {user_commits} commits",
                "Championed technical excellence, contributing {user_commit_percent}% of commits while utilizing {frameworks}",
            ],
            'coding_solo_stats': [
                # Solo development with metrics
                "Developed application using {primary_language} and {frameworks}, implementing {skills}",
                "Built application independently, writing {total_commits} commits across {date_range}",
                "Created application with {code_files} code files, utilizing {languages} and {frameworks}",
                "Implemented solution focusing on {skills}, delivering {total_commits} commits",
                "Designed and developed application using {primary_language}, demonstrating expertise in {skills}",
                "Engineered application from concept to completion, implementing {skills} with {frameworks}",
                "Constructed full-stack application using {languages}, completing {total_commits} commits",
                "Delivered application with {code_files} code files, showcasing proficiency in {primary_language}",
                "Executed end-to-end development, leveraging {frameworks} and {skills}",
                "Produced application through {total_commits} iterative commits, utilizing {languages} and {frameworks}",
                "Crafted solution with emphasis on {skills}, completing development across {date_range}",
                "Established codebase with {code_files} files, demonstrating {primary_language} expertise",
            ],
            'coding_generic': [
                # Coding projects without git stats - more variety
                "Developed application using {primary_language} and {frameworks}, implementing {skills}",
                "Built solution utilizing {languages} and {frameworks}",
                "Created application with {code_files} code files, focusing on {skills}",
                "Implemented application using {primary_language}, demonstrating {skills}",
                "Designed and developed solution with {frameworks} and {languages}",
                "Engineered application leveraging {primary_language} and {frameworks}",
                "Constructed application with focus on {skills} and modern {frameworks}",
                "Delivered application utilizing {languages} to implement {skills}",
                "Produced software solution with {primary_language} and {frameworks}",
                "Established application using {languages}, emphasizing {skills}",
                "Executed development with {primary_language}, incorporating {frameworks}",
                "Formulated solution demonstrating proficiency in {skills}",
            ],
            'writing': [
                # General writing templates
                "Created written content, producing {file_count} documents and articles",
                "Developed written content, generating {file_count} text files",
                "Authored content, producing {file_count} documents across {date_range}",
                "Produced written materials, creating {file_count} content files",
                "Wrote and edited content, delivering {file_count} documents",
                "Composed comprehensive documentation, creating {file_count} files",
                "Drafted technical content, producing {file_count} documents",
                "Generated {file_count} written deliverables",
                "Crafted documentation suite comprising {file_count} files",
                "Compiled content library with {file_count} documents across {date_range}",
                # Research & Academic writing
                "Conducted research and authored content, developing comprehensive analysis across {file_count} documents",
                "Synthesized research findings, producing scholarly content in {file_count} files",
                "Performed literature review and analysis, documenting findings in {file_count} research files",
                "Developed academic manuscript, creating {file_count} research documents with citations and methodology",
                "Authored research paper, conducting empirical analysis and documenting results across {date_range}",
                "Compiled bibliographic research, organizing {file_count} source documents and annotations",
                # Technical documentation
                "Engineered comprehensive technical documentation, creating {file_count} user guides and API references",
                "Developed API documentation, producing {file_count} reference files and integration guides",
                "Authored technical specifications, delivering {file_count} detailed documentation files",
                "Created user manuals and guides, producing {file_count} instructional documents",
                "Documented software architecture, generating {file_count} technical design files",
                "Produced developer documentation, crafting {file_count} tutorial and reference files",
                # Editorial & content strategy
                "Edited and refined content, revising {file_count} documents for clarity and coherence",
                "Developed content strategy, organizing {file_count} documents with consistent style guidelines",
                "Copyedited materials, improving readability across {file_count} written pieces",
                "Curated and organized content library, managing {file_count} editorial files",
            ],
            'art': [
                # General design templates
                "Designed visual assets, creating {file_count} graphics and visual elements",
                "Developed visual content, producing {file_count} image files",
                "Created artistic work, generating {file_count} design assets",
                "Designed visuals, producing {file_count} creative assets across {date_range}",
                "Produced visual designs, creating {file_count} image files",
                "Crafted {file_count} graphic elements",
                "Established visual identity with {file_count} design assets",
                "Generated creative materials, producing {file_count} visual files",
                "Conceptualized and executed {file_count} designs",
                # Graphic design & branding
                "Designed brand identity, developing {file_count} visual assets with cohesive aesthetic",
                "Created graphic design suite, producing {file_count} marketing and branding materials",
                "Developed typography and layout, crafting {file_count} design compositions",
                "Engineered visual branding, creating {file_count} logo variations and style guide assets",
                "Designed user interface mockups, producing {file_count} high-fidelity design files",
                "Crafted print and digital designs, developing {file_count} publication-ready assets",
                # Photo editing & retouching
                "Performed photo retouching, editing and enhancing {file_count} image files",
                "Executed color correction and grading, processing {file_count} photographs",
                "Applied advanced compositing techniques, producing {file_count} edited images",
                "Enhanced visual quality of imagery, retouching {file_count} photos with professional techniques",
                "Conducted photo manipulation, creating {file_count} edited and refined images",
                "Performed image restoration and enhancement, processing {file_count} visual files",
                # Digital illustration & 3D
                "Illustrated visuals, creating {file_count} custom digital artworks",
                "Produced digital paintings, developing {file_count} original illustration files",
                "Created 3D renders and visualizations, generating {file_count} dimensional assets",
                "Designed vector graphics, producing {file_count} scalable illustration files",
            ],
            'generic': [
                "Worked on application development",
                "Contributed to software development",
                "Participated in project implementation",
                "Engaged in application development",
                "Collaborated on software project",
            ]
        }
    
    def _get_contextual_templates(self, context: Dict) -> List[str]:
        """
        Generate contextual templates based on specific skills, languages, and frameworks.
        These templates are triggered by specific combinations in the project data.
        
        Args:
            context: Template context with project data
            
        Returns:
            List of contextual template strings
        """
        contextual = []
        # Use all_frameworks/all_languages for matching (includes all, not just top 3)
        frameworks = context.get('all_frameworks', context.get('frameworks', '')).lower()
        languages = context.get('all_languages', context.get('languages', '')).lower()
        skills = context.get('skills', '').lower()
        
        # Framework/Technology explanation templates - help recruiters understand what they're used for
        # Use template strings for consistency with base templates
        # Machine Learning / AI Frameworks
        if 'tensorflow' in frameworks:
            contextual.append("Utilized TensorFlow framework to implement machine learning models and neural network architectures")
        if 'pytorch' in frameworks:
            contextual.append("Leveraged PyTorch deep learning framework for neural network development and model training")
        if 'scikit-learn' in frameworks or 'sklearn' in frameworks:
            contextual.append("Applied scikit-learn machine learning library for predictive modeling and data analysis")
        if 'keras' in frameworks:
            contextual.append("Implemented Keras neural network API for streamlined deep learning model development")
        
        # Data Science Frameworks
        if 'pandas' in frameworks:
            contextual.append("Employed Pandas data manipulation library for structured data analysis and transformation")
        if 'numpy' in frameworks:
            contextual.append("Utilized NumPy numerical computing library for efficient array operations and mathematical computations")
        if 'matplotlib' in frameworks or 'seaborn' in frameworks:
            contextual.append("Created data visualizations using Matplotlib/Seaborn for analytical insights and reporting")
        
        # Web Frontend Frameworks
        if 'react' in frameworks:
            contextual.append("Built interactive user interface using React JavaScript library with component-based architecture")
        if 'angular' in frameworks:
            contextual.append("Developed single-page application with Angular TypeScript framework and reactive programming")
        if 'vue' in frameworks or 'vue.js' in frameworks:
            contextual.append("Constructed progressive web interface using Vue.js framework for enhanced interactivity")
        if 'next.js' in frameworks or 'nextjs' in frameworks:
            contextual.append("Implemented server-side rendering with Next.js React framework for optimized performance and SEO")
        if 'svelte' in frameworks:
            contextual.append("Built reactive user interface using Svelte framework with compile-time optimization")
        
        # Backend Frameworks
        if 'django' in frameworks:
            contextual.append("Developed backend infrastructure using Django Python web framework with built-in ORM and admin interface")
        if 'flask' in frameworks:
            contextual.append("Built lightweight web application backend with Flask Python microframework for RESTful services")
        if 'express' in frameworks or 'express.js' in frameworks:
            contextual.append("Implemented Node.js backend using Express.js framework for fast, scalable server-side applications")
        if 'spring' in frameworks or 'spring boot' in frameworks:
            contextual.append("Architected enterprise Java backend with Spring Boot framework for dependency injection and microservices")
        if 'fastapi' in frameworks:
            contextual.append("Developed high-performance API using FastAPI Python framework with automatic documentation generation")
        if 'nest' in frameworks or 'nestjs' in frameworks:
            contextual.append("Built scalable server-side application with NestJS TypeScript framework using modular architecture")
        if 'laravel' in frameworks:
            contextual.append("Developed web application backend using Laravel PHP framework with elegant MVC architecture")
        if 'ruby on rails' in frameworks or 'rails' in frameworks:
            contextual.append("Built full-stack web application with Ruby on Rails framework following convention-over-configuration principles")
        
        # Mobile Frameworks
        if 'react native' in frameworks:
            contextual.append("Developed cross-platform mobile application using React Native framework for iOS and Android deployment")
        if 'flutter' in frameworks:
            contextual.append("Built native mobile application with Flutter framework using Dart for multi-platform development")
        if 'ionic' in frameworks:
            contextual.append("Created hybrid mobile app using Ionic framework for cross-platform deployment with web technologies")
        
        # Database Frameworks/ORMs
        if 'sqlalchemy' in frameworks:
            contextual.append("Implemented database layer using SQLAlchemy ORM for Python-based data persistence and queries")
        if 'mongoose' in frameworks:
            contextual.append("Designed MongoDB data models using Mongoose ODM for schema validation and data relationships")
        if 'sequelize' in frameworks:
            contextual.append("Configured relational database integration with Sequelize ORM for Node.js data management")
        if 'prisma' in frameworks:
            contextual.append("Established type-safe database access using Prisma ORM with auto-generated queries and migrations")
        
        # Testing Frameworks
        if 'jest' in frameworks:
            contextual.append("Implemented comprehensive test suite using Jest testing framework for JavaScript unit and integration tests")
        if 'pytest' in frameworks:
            contextual.append("Developed automated testing with pytest framework for Python test coverage and fixtures")
        if 'junit' in frameworks:
            contextual.append("Created unit tests using JUnit framework for Java test-driven development")
        if 'mocha' in frameworks or 'chai' in frameworks:
            contextual.append("Established testing infrastructure with Mocha/Chai frameworks for Node.js test assertions")
        
        # Cloud & DevOps Tools
        if 'docker' in frameworks:
            contextual.append("Containerized application using Docker for consistent deployment across environments")
        if 'kubernetes' in frameworks or 'k8s' in frameworks:
            contextual.append("Orchestrated containerized deployment with Kubernetes for automated scaling and management")
        if 'terraform' in frameworks:
            contextual.append("Automated infrastructure provisioning using Terraform for cloud resource management as code")
        if 'jenkins' in frameworks:
            contextual.append("Configured continuous integration pipeline with Jenkins for automated build and deployment")
        if 'github actions' in frameworks or 'gitlab ci' in frameworks:
            contextual.append("Implemented CI/CD automation using GitHub Actions/GitLab CI for streamlined development workflow")
        
        # State Management
        if 'redux' in frameworks:
            contextual.append("Managed application state using Redux library for predictable state container and data flow")
        if 'mobx' in frameworks:
            contextual.append("Implemented reactive state management with MobX library for simplified data synchronization")
        if 'vuex' in frameworks:
            contextual.append("Centralized state management using Vuex library for Vue.js application data handling")
        
        # GraphQL
        if 'graphql' in frameworks or 'apollo' in frameworks:
            contextual.append("Developed flexible API using GraphQL query language for efficient data fetching and manipulation")
        
        # Real-time Communication
        if 'socket.io' in frameworks or 'websocket' in frameworks:
            contextual.append("Implemented real-time bidirectional communication using WebSocket/Socket.io for live data updates")
        
        # Game Development
        if 'unity' in frameworks:
            contextual.append("Developed interactive game/simulation using Unity engine with C# scripting")
        if 'unreal' in frameworks:
            contextual.append("Built high-fidelity 3D application with Unreal Engine for advanced graphics and physics")
        
        # Content Management
        if 'wordpress' in frameworks:
            contextual.append("Developed content management solution using WordPress CMS with custom themes and plugins")
        if 'strapi' in frameworks:
            contextual.append("Built headless CMS using Strapi for flexible content delivery and API generation")
        
        # Programming Language explanations (when language might be unfamiliar)
        if 'rust' in languages:
            contextual.append("Utilized Rust systems programming language ensuring memory safety and high performance")
        if 'go' in languages or 'golang' in languages:
            contextual.append("Implemented application using Go language for efficient concurrent processing and cloud-native development")
        if 'kotlin' in languages:
            contextual.append("Developed application with Kotlin language for modern Android development with null-safety features")
        if 'swift' in languages:
            contextual.append("Built iOS application using Swift programming language for native Apple platform development")
        if 'scala' in languages:
            contextual.append("Leveraged Scala functional programming language with JVM compatibility and concurrency support")
        if 'elixir' in languages:
            contextual.append("Developed scalable application using Elixir language for fault-tolerant distributed systems")
        if 'clojure' in languages:
            contextual.append("Implemented application with Clojure functional language for immutable data structures and concurrency")
        
        # Web Development templates (general)
        if any(fw in frameworks for fw in ['react', 'angular', 'vue', 'next.js', 'django', 'flask', 'express', 'spring']):
            contextual.extend([
                "Engineered full-stack web application with modern frameworks and responsive design principles",
                "Developed dynamic web interface ensuring cross-browser compatibility and optimal user experience",
                "Built scalable web application with RESTful API architecture and efficient data management",
            ])
        
        # Database templates - be specific to avoid matching "data science" or "data analysis"
        if any(skill in skills for skill in ['database', 'sql']) or any(fw in frameworks for fw in ['postgresql', 'mysql', 'mongodb', 'redis', 'sqlalchemy', 'sequelize', 'mongoose', 'prisma']):
            contextual.extend([
                "Implemented robust database architecture, optimizing queries for performance and scalability",
                "Designed efficient data models ensuring data integrity and normalized schema structure",
                "Integrated database solutions with optimized indexing and query performance",
            ])
        
        # Object-Oriented Programming
        if 'object-oriented' in skills or any(lang in languages for lang in ['java', 'c++', 'python', 'c#']):
            contextual.append("Applied object-oriented design principles, implementing inheritance, polymorphism, and encapsulation")
        
        # API Development
        if 'api' in skills or 'restful' in skills or 'rest' in frameworks.lower():
            contextual.extend([
                "Developed RESTful API endpoints with comprehensive documentation and error handling",
                "Built secure API infrastructure implementing authentication and rate limiting",
            ])
        
        # Testing & Quality
        if any(skill in skills for skill in ['testing', 'test', 'quality']):
            contextual.extend([
                "Implemented comprehensive test suite achieving high code coverage and reliability",
                "Established testing framework including unit, integration, and end-to-end tests",
            ])
        
        # Frontend specific
        if any(fw in frameworks for fw in ['react', 'angular', 'vue', 'next.js']):
            contextual.extend([
                "Created responsive user interface utilizing component-based architecture",
                "Built interactive frontend with state management and optimized rendering",
            ])
        
        # Backend specific
        if any(fw in frameworks for fw in ['django', 'flask', 'express', 'spring', 'fastapi']):
            contextual.extend([
                "Architected server-side infrastructure with scalable microservices pattern",
                "Developed backend services implementing business logic and data processing",
            ])
        
        # Python specific
        if 'python' in languages:
            contextual.extend([
                "Leveraged Python ecosystem, utilizing libraries for efficient data processing",
                "Implemented application with Python, emphasizing clean code and Pythonic best practices",
            ])
        
        # JavaScript/TypeScript specific
        if 'javascript' in languages:
            contextual.extend([
                "Developed application with modern JavaScript/ES6+ features and asynchronous programming patterns",
            ])

        if  'typescript' in languages:
            contextual.extend([
                "Built application utilizing TypeScript for type-safe code and improved maintainability",
            ])


        
        # Mobile development
        if any(fw in frameworks for fw in ['react native', 'flutter', 'swift', 'kotlin']):
            contextual.append("Developed cross-platform mobile application with native performance characteristics")
        
        # Cloud & DevOps
        if any(skill in skills for skill in ['cloud', 'devops', 'deployment', 'ci/cd']):
            contextual.extend([
                "Deployed application to cloud infrastructure with automated CI/CD pipeline and monitoring",
                "Configured containerized deployment ensuring scalability and reliability",
            ])
        
        # Security
        if 'security' in skills or 'authentication' in skills:
            contextual.extend([
                "Implemented security measures including authentication, authorization, and data encryption",
                "Enhanced security posture with input validation and protection against common vulnerabilities",
            ])
        
        # Performance optimization
        if 'performance' in skills or 'optimization' in skills:
            contextual.extend([
                "Optimized application performance through code profiling, caching strategies, and efficient algorithms",
                "Improved response times by implementing performance best practices and bottleneck resolution",
            ])
        
        # Algorithms & Data Structures
        if 'algorithm' in skills or 'data structure' in skills:
            contextual.append("Implemented efficient algorithms and data structures for optimal computational complexity")
        
        # Git/Version Control
        if context.get('total_commits', 0) > 0:
            contextual.append("Maintained comprehensive version control with detailed commit history and branching strategy")
        
        # Writing & Documentation Tools
        if 'latex' in frameworks or 'tex' in frameworks:
            contextual.append("Authored academic manuscript using LaTeX typesetting system for professional document formatting and mathematical notation")
        if 'markdown' in frameworks or 'md' in frameworks:
            contextual.append("Documented application using Markdown markup language for clean, readable technical documentation")
        if 'sphinx' in frameworks or 'readthedocs' in frameworks:
            contextual.append("Generated comprehensive documentation with Sphinx documentation generator for structured technical guides")
        if 'confluence' in frameworks or 'wiki' in frameworks:
            contextual.append("Organized knowledge base using collaborative wiki platform for team documentation and information sharing")
        if 'jira' in frameworks or 'asana' in frameworks:
            contextual.append("Coordinated project documentation integrating with project management tools for comprehensive workflow documentation")
        
        # Research & Academic
        if 'research' in skills or 'academic' in skills or 'paper' in skills:
            contextual.extend([
                "Conducted systematic literature review, synthesizing findings from scholarly sources to inform research direction",
                "Performed empirical analysis, employing rigorous methodology and statistical validation",
                "Authored peer-reviewed research, contributing original findings to academic discourse",
            ])
        
        # Technical Writing
        if 'documentation' in skills or 'technical writing' in skills or 'api documentation' in skills:
            contextual.extend([
                "Engineered technical documentation suite, creating user guides, API references, and system architecture documentation",
                "Developed comprehensive SDK documentation, enabling efficient developer integration and adoption",
                "Authored clear technical specifications, translating complex systems into accessible documentation",
            ])
        
        # Content Strategy & Editorial
        if 'content strategy' in skills or 'editorial' in skills or 'copywriting' in skills:
            contextual.extend([
                "Crafted content strategy, organizing information architecture for optimal user engagement",
                "Edited and refined written materials, ensuring consistency, clarity, and adherence to style guidelines",
                "Developed editorial calendar, managing content workflow and publication schedule",
            ])
        
        # Design Tools - Adobe Suite
        if 'photoshop' in frameworks or 'ps' in frameworks or 'adobe photoshop' in frameworks:
            contextual.append("Executed advanced photo editing using Adobe Photoshop for retouching, compositing, and color correction")
        if 'illustrator' in frameworks or 'ai' in frameworks or 'adobe illustrator' in frameworks:
            contextual.append("Created vector graphics using Adobe Illustrator for scalable logos, icons, and illustrations")
        if 'indesign' in frameworks or 'adobe indesign' in frameworks:
            contextual.append("Designed publication layouts using Adobe InDesign for professional print and digital typography")
        if 'after effects' in frameworks or 'adobe after effects' in frameworks:
            contextual.append("Produced motion graphics using Adobe After Effects for animated visual content")
        if 'premiere' in frameworks or 'adobe premiere' in frameworks:
            contextual.append("Edited video content using Adobe Premiere Pro for professional post-production workflow")
        if 'lightroom' in frameworks or 'adobe lightroom' in frameworks:
            contextual.append("Processed and color-graded photography using Adobe Lightroom for professional image enhancement")
        
        # Design Tools - Open Source
        if 'gimp' in frameworks:
            contextual.append("Performed image editing using GIMP open-source software for photo manipulation and retouching")
        if 'inkscape' in frameworks:
            contextual.append("Designed vector graphics using Inkscape for scalable illustration and logo design")
        if 'krita' in frameworks:
            contextual.append("Created digital paintings using Krita for professional illustration and concept art")
        if 'blender' in frameworks:
            contextual.append("Developed 3D models and renders using Blender for photorealistic visualization and animation")
        
        # Design Tools - UI/UX
        if 'figma' in frameworks:
            contextual.append("Designed user interface using Figma collaborative design platform for interactive prototyping")
        if 'sketch' in frameworks:
            contextual.append("Created UI/UX designs using Sketch vector-based design tool for digital interfaces")
        if 'adobe xd' in frameworks or 'xd' in frameworks:
            contextual.append("Prototyped user experience using Adobe XD for wireframing and interactive design")
        
        # Graphic Design & Visual Communication
        if 'graphic design' in skills or 'visual design' in skills or 'branding' in skills:
            contextual.extend([
                "Developed cohesive brand identity, establishing visual guidelines and design system for consistent communication",
                "Created compelling visual compositions utilizing principles of typography, color theory, and layout design",
                "Designed marketing collateral, producing print and digital materials aligned with brand strategy",
            ])
        
        # Photography & Retouching
        if 'photography' in skills or 'photo editing' in skills or 'retouching' in skills:
            contextual.extend([
                "Executed professional photo retouching, enhancing image quality through advanced editing techniques",
                "Performed color grading and correction, establishing consistent visual aesthetic across image collection",
                "Conducted image compositing, seamlessly blending multiple photographic elements into cohesive visuals",
            ])
        
        # 3D & Animation
        if '3d modeling' in skills or 'animation' in skills or '3d' in skills:
            contextual.extend([
                "Modeled 3D assets, creating detailed geometry with proper topology and UV mapping",
                "Rendered photorealistic visualizations, utilizing advanced lighting and material techniques",
                "Animated visual sequences, implementing keyframe animation and procedural motion",
            ])
        
        # Digital Illustration
        if 'illustration' in skills or 'digital art' in skills or 'concept art' in skills:
            contextual.extend([
                "Illustrated original artwork, demonstrating strong understanding of composition, anatomy, and perspective",
                "Created concept art, visualizing ideas through iterative sketching and digital painting techniques",
                "Developed digital illustrations with attention to color harmony and visual storytelling",
            ])
        
        return contextual


# Convenience function for easy import
def generate_resume_items(
    project_data: Dict[str, Any], 
    user_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate resume bullet points for a project.
    
    This is a convenience function that creates a ResumeItemGenerator instance
    and calls generate_resume_items. Use this for simple one-off generation.
    
    Args:
        project_data: Project data dictionary
        user_name: Optional username for user-specific stats
        
    Returns:
        Dict with items list and generated_at timestamp
    """
    generator = ResumeItemGenerator()
    return generator.generate_resume_items(project_data, user_name)

