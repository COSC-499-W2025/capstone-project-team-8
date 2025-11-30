"""
Resume Item Generator Service

This module generates professional resume bullet points for projects based on
detected skills, languages, frameworks, project classification, git contribution
statistics, and content analysis. The service uses a category-based approach
to ensure comprehensive, non-overlapping bullet points.

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
    
    Uses a category-based generation approach:
    1. Framework-specific contextual templates (detailed explanations)
    2. Category-based bullets (languages, frameworks, skills, content, git, etc.)
    
    This ensures comprehensive coverage without overlap.
    """
    
    def __init__(self):
        """Initialize the resume item generator."""
        pass
    
    def generate_resume_items(
        self, 
        project_data: Dict[str, Any], 
        user_name: Optional[str] = None,
        content_summary: Optional[Any] = None  # ProjectContentSummary from content_analyzer
    ) -> Dict[str, Any]:
        """
        Generate comprehensive, non-overlapping resume bullet points for a project.
        
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
            content_summary: Optional ProjectContentSummary from content analyzer
            
        Returns:
            Dict with:
                - items: List of resume bullet point strings
                - generated_at: Timestamp when items were generated
        """
        try:
            bullets = []
            
            # Extract project metadata
            classification = project_data.get('classification') or {}
            languages = classification.get('languages', []) if isinstance(classification, dict) else []
            frameworks = classification.get('frameworks', []) if isinstance(classification, dict) else []
            skills = classification.get('resume_skills', []) if isinstance(classification, dict) else []
            
            # Extract file counts
            files = project_data.get('files', {})
            code_files = len(files.get('code', []))
            
            # Build context for framework templates
            context = self._build_context(project_data, user_name)
            
            # CATEGORY 1: Framework-specific contextual templates (detailed explanations)
            framework_bullets = self._get_contextual_templates(context)
            bullets.extend(framework_bullets)
            
            # Track what frameworks/languages/skills were covered by contextual templates
            covered = self._get_covered_items(framework_bullets, frameworks, languages, skills)
            
            # CATEGORY 2: Languages (if not fully covered by contextual templates)
            if languages and not self._all_covered(languages, covered['languages']):
                lang_bullet = self._generate_languages_bullet(languages, covered['languages'])
                if lang_bullet:
                    bullets.append(lang_bullet)
            
            # CATEGORY 3: Frameworks (if not fully covered by contextual templates)
            if frameworks and not self._all_covered(frameworks, covered['frameworks']):
                fw_bullet = self._generate_frameworks_bullet(frameworks, covered['frameworks'])
                if fw_bullet:
                    bullets.append(fw_bullet)
            
            # CATEGORY 4: Skills (if not fully covered)
            if skills and not self._all_covered(skills, covered['skills']):
                skill_bullet = self._generate_skills_bullet(skills, covered['skills'])
                if skill_bullet:
                    bullets.append(skill_bullet)
            
            # CATEGORY 5: Content Volume (from content analysis)
            if content_summary and content_summary.total_documents > 0:
                content_bullet = self._generate_content_volume_bullet(content_summary)
                if content_bullet:
                    bullets.append(content_bullet)
            
            # CATEGORY 6: Content Type
            if content_summary:
                type_bullet = self._generate_content_type_bullet(content_summary)
                if type_bullet:
                    bullets.append(type_bullet)
            
            # CATEGORY 7: Topics
            if content_summary and content_summary.primary_topics:
                topics_bullet = self._generate_topics_bullet(content_summary.primary_topics)
                if topics_bullet:
                    bullets.append(topics_bullet)
            
            # CATEGORY 8: Structural Features
            if content_summary:
                struct_bullet = self._generate_structural_features_bullet(content_summary)
                if struct_bullet:
                    bullets.append(struct_bullet)
            
            # CATEGORY 9: Writing Quality (only if advanced)
            if content_summary:
                quality_bullet = self._generate_writing_quality_bullet(content_summary)
                if quality_bullet:
                    bullets.append(quality_bullet)
            
            # CATEGORY 10: Code Metrics (if code files exist)
            if code_files > 0:
                code_bullet = self._generate_code_metrics_bullet(code_files)
                if code_bullet:
                    bullets.append(code_bullet)
            
            # CATEGORY 11: Git Contributions
            git_bullet = self._generate_git_contribution_bullet(project_data, user_name)
            if git_bullet:
                bullets.append(git_bullet)
            
            # CATEGORY 12: Project Scale (if substantial)
            scale_bullet = self._generate_project_scale_bullet(project_data)
            if scale_bullet:
                bullets.append(scale_bullet)
            
            # Fallback: If no bullets generated, add a generic one
            if not bullets:
                bullets.append("Worked on project development")
            
            return {
                'items': bullets,
                'generated_at': int(datetime.now().timestamp())
            }
            
        except Exception as e:
            logger.error(f"Error generating resume items: {e}", exc_info=True)
            return {
                'items': [],
                'generated_at': int(datetime.now().timestamp())
            }
    
    def _build_context(self, project_data: Dict, user_name: Optional[str]) -> Dict:
        """Build template context for framework-specific templates."""
        classification = project_data.get('classification') or {}
        languages = classification.get('languages', []) if isinstance(classification, dict) else []
        frameworks = classification.get('frameworks', []) if isinstance(classification, dict) else []
        skills = classification.get('resume_skills', []) if isinstance(classification, dict) else []
        files = project_data.get('files', {})
        contributors = project_data.get('contributors', [])
        
        if not isinstance(contributors, list): 
            contributors = []

        git_stats = self._extract_user_contributions(contributors, user_name)
        
        return {
            'primary_language': languages[0] if languages else '',
            'languages': ', '.join(languages[:3]) if languages else '',
            'frameworks': ', '.join(frameworks[:3]) if frameworks else '',
            'all_frameworks': ', '.join(frameworks) if frameworks else '',
            'all_languages': ', '.join(languages) if languages else '',
            'skills': ', '.join(skills[:5]) if skills else '',
            'code_files': len(files.get('code', [])) if isinstance(files, dict) else 0,
            'file_count': sum(len(files.get(k, [])) for k in ['code', 'content', 'image', 'unknown']) if isinstance(files, dict) else 0,
            'is_collaborative': project_data.get('collaborative', False),
            'contributor_count': len([c for c in contributors if isinstance(c, dict) and c.get('commits', 0) > 0]),
            **git_stats
        }
    
    def _get_covered_items(
        self, 
        bullets: List[str], 
        frameworks: List[str], 
        languages: List[str], 
        skills: List[str]
    ) -> Dict[str, List[str]]:
        """Extract which frameworks, languages, and skills are mentioned in contextual bullets."""
        covered = {'frameworks': [], 'languages': [], 'skills': []}
        text_lower = ' '.join(bullets).lower()
        
        for fw in frameworks:
            if fw.lower() in text_lower:
                covered['frameworks'].append(fw)
        for lang in languages:
            if lang.lower() in text_lower:
                covered['languages'].append(lang)
        for skill in skills:
            if skill.lower() in text_lower:
                covered['skills'].append(skill)
        
        return covered
    
    def _all_covered(self, items: List[str], covered: List[str]) -> bool:
        """Check if all items are covered."""
        if not items:
            return True
        return len(covered) >= len(items) and all(item in covered for item in items)
    
    def _generate_languages_bullet(self, languages: List[str], covered: List[str]) -> Optional[str]:
        """Generate languages bullet (only uncovered languages)."""
        uncovered = [l for l in languages if l not in covered]
        if not uncovered:
            return None
        
        if len(uncovered) == 1:
            return f"Developed using {uncovered[0]}"
        elif len(uncovered) == 2:
            return f"Developed using {uncovered[0]} and {uncovered[1]}"
        else:
            lang_str = ', '.join(uncovered[:4])
            if len(uncovered) > 4:
                lang_str += f", and {len(uncovered) - 4} more"
            return f"Developed using {lang_str}"
    
    def _generate_frameworks_bullet(self, frameworks: List[str], covered: List[str]) -> Optional[str]:
        """Generate frameworks bullet (only uncovered frameworks)."""
        uncovered = [f for f in frameworks if f not in covered]
        if not uncovered:
            return None
        
        if len(uncovered) == 1:
            return f"Built with {uncovered[0]}"
        elif len(uncovered) == 2:
            return f"Built with {uncovered[0]} and {uncovered[1]}"
        else:
            fw_str = ', '.join(uncovered[:4])
            if len(uncovered) > 4:
                fw_str += f", and {len(uncovered) - 4} more"
            return f"Built with {fw_str}"
    
    def _generate_skills_bullet(self, skills: List[str], covered: List[str]) -> Optional[str]:
        """Generate skills bullet (only uncovered skills)."""
        uncovered = [s for s in skills if s not in covered]
        if not uncovered:
            return None
        
        if len(uncovered) <= 5:
            skills_str = ', '.join(uncovered)
        else:
            skills_str = ', '.join(uncovered[:5]) + f", and {len(uncovered) - 5} more"
        return f"Demonstrated skills in {skills_str}"
    
    def _generate_content_volume_bullet(self, summary: Any) -> Optional[str]:
        """Generate bullet for content volume."""
        if summary.total_documents == 1:
            doc_type_plural = self._pluralize_doc_type(summary.primary_document_type)
            return f"Authored {summary.total_words:,}-word {doc_type_plural[:-1]}"
        else:
            doc_type_plural = self._pluralize_doc_type(summary.primary_document_type)
            return f"Authored {summary.total_words:,} words across {summary.total_documents} {doc_type_plural}"
    
    def _generate_content_type_bullet(self, summary: Any) -> Optional[str]:
        """Generate bullet for document types."""
        doc_types = summary.document_types
        
        if len(doc_types) == 1:
            type_name = self._format_doc_type_name(summary.primary_document_type)
            return f"Created {type_name}"
        elif len(doc_types) > 1:
            type_names = [self._format_doc_type_name(k) for k in doc_types.keys()]
            return f"Created {self._format_list(type_names)}"
        return None
    
    def _generate_topics_bullet(self, topics: List[str]) -> Optional[str]:
        """Generate bullet for topics covered."""
        if not topics:
            return None
        
        if len(topics) == 1:
            return f"Covered topic: {topics[0]}"
        elif len(topics) == 2:
            return f"Covered topics: {topics[0]} and {topics[1]}"
        else:
            topics_str = ', '.join(topics[:4])
            if len(topics) > 4:
                topics_str += f", and {len(topics) - 4} more"
            return f"Covered topics including {topics_str}"
    
    def _generate_structural_features_bullet(self, summary: Any) -> Optional[str]:
        """Generate bullet for structural features."""
        features = []
        if summary.has_citations:
            features.append("citations")
        if summary.has_code_examples:
            features.append("code examples")
        if summary.has_mathematical_content:
            features.append("mathematical notation")
        
        if not features:
            return None
        
        return f"Featured {self._format_list(features)}"
    
    def _generate_writing_quality_bullet(self, summary: Any) -> Optional[str]:
        """Generate bullet for writing quality (only if advanced)."""
        if summary.primary_complexity == 'advanced' and summary.vocabulary_richness > 0.6:
            return (
                f"Produced {summary.primary_complexity} complexity writing "
                f"with {summary.vocabulary_richness:.1%} vocabulary richness"
            )
        return None
    
    def _generate_code_metrics_bullet(self, code_files: int) -> Optional[str]:
        """Generate bullet for code file count."""
        if code_files == 1:
            return f"Developed {code_files} code file"
        else:
            return f"Developed {code_files} code files"
    
    def _generate_git_contribution_bullet(
        self, 
        project_data: Dict, 
        user_name: Optional[str]
    ) -> Optional[str]:
        """Generate bullet for git contributions."""
        contributors = project_data.get('contributors', [])
        git_stats = self._extract_user_contributions(contributors, user_name)
        
        if 'user_commits' in git_stats:
            return (
                f"Contributed {git_stats['user_commit_percent']:.1f}% of commits "
                f"({git_stats['user_commits']} commits, {git_stats['user_lines_added']:,} lines added)"
            )
        elif git_stats.get('total_commits', 0) > 0:
            return f"Maintained version control with {git_stats['total_commits']} commits"
        
        return None
    
    def _generate_project_scale_bullet(self, project_data: Dict) -> Optional[str]:
        """Generate bullet for project scale."""
        files = project_data.get('files', {})
        total_files = sum(len(files.get(k, [])) for k in ['code', 'content', 'image', 'unknown'])
        
        file_types = []
        if files.get('code'):
            file_types.append('code')
        if files.get('content'):
            file_types.append('content')
        if files.get('image'):
            file_types.append('image')
        
        if total_files > 20 and len(file_types) > 1:
            return (
                f"Managed project with {total_files} files across "
                f"{self._format_list(file_types)} files"
            )
        return None
    
    def _format_list(self, items: List[str]) -> str:
        """Format list with proper commas and 'and'."""
        if len(items) == 1:
            return items[0]
        elif len(items) == 2:
            return f"{items[0]} and {items[1]}"
        else:
            return f"{', '.join(items[:-1])}, and {items[-1]}"
    
    def _pluralize_doc_type(self, doc_type: str) -> str:
        """Convert document type to plural form."""
        plural_map = {
            'research_paper': 'research papers',
            'technical_documentation': 'technical documents',
            'blog_post': 'blog posts',
            'creative_writing': 'creative writing pieces',
            'general_article': 'articles'
        }
        return plural_map.get(doc_type, f"{doc_type}s")
    
    def _format_doc_type_name(self, doc_type: str) -> str:
        """Format document type name for display."""
        name_map = {
            'research_paper': 'research papers',
            'technical_documentation': 'technical documentation',
            'blog_post': 'blog posts',
            'creative_writing': 'creative writing',
            'general_article': 'articles'
        }
        return name_map.get(doc_type, doc_type.replace('_', ' '))
    
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
        
        
        if not isinstance(contributors, list):
            return {}
        
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
        
        # Database templates
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

        if 'typescript' in languages:
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
    user_name: Optional[str] = None,
    content_summary: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Generate resume bullet points for a project.
    
    This is a convenience function that creates a ResumeItemGenerator instance
    and calls generate_resume_items. Use this for simple one-off generation.
    
    Args:
        project_data: Project data dictionary
        user_name: Optional username for user-specific stats
        content_summary: Optional ProjectContentSummary from content analyzer
        
    Returns:
        Dict with items list and generated_at timestamp
    """
    generator = ResumeItemGenerator()
    return generator.generate_resume_items(project_data, user_name, content_summary)
