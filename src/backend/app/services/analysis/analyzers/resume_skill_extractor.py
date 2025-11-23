"""
Skill Extraction Module

This module extracts professional skills from detected languages, frameworks,
and file types in a project. It provides intelligent skill inference that goes
beyond simple detection to understand what capabilities are demonstrated.

Main functions:
    - extract_skills(): Extract all skills from a project
    - extract_skills_from_languages(): Get skills from programming languages
    - extract_skills_from_frameworks(): Get skills from frameworks/libraries
    - extract_skills_from_files(): Get skills from file types (design, media, etc.)
"""

import os
from pathlib import Path
from typing import List, Set, Union
from collections import Counter


# Language to skills mapping
# NOTE: Language-specific programming skills are removed because languages are listed
# separately in the response. Skills here focus on concepts, paradigms, and specializations.
LANGUAGE_SKILLS = {
    # General Purpose Languages - Only paradigm/concept skills
    'Python': [],  # Programming skill removed, let frameworks add context
    'Java': ['Object-Oriented Programming'],
    'C#': ['Object-Oriented Programming'],
    'Go': [],
    'Rust': [],
    'PHP': [],
    'Ruby': [],
    'Kotlin': ['Object-Oriented Programming'],
    'Scala': ['Functional Programming'],
    'Elixir': ['Functional Programming'],
    'Erlang': ['Functional Programming'],
    
    # Frontend Languages - Skills from frameworks, not languages
    'JavaScript': [],
    'TypeScript': [],
    'HTML': [],
    'CSS': [],
    
    # Mobile Languages
    'Swift': ['iOS Development'],
    'Dart': [],  # Let Flutter framework add Mobile Development
    
    # Systems & Low-Level
    'C': [],
    'C++': ['Object-Oriented Programming'],
    'Assembly': [],
    
    # Data & Scientific - These DO imply specific domains
    'R': ['Statistical Analysis'],
    'Julia': ['Scientific Computing'],
    'MATLAB': ['Scientific Computing'],
    
    # Scripting Languages - Automation is the skill
    'Shell': ['Automation'],
    'PowerShell': ['Automation'],
    'Batch': ['Automation'],
    'Perl': [],
    'Lua': [],
    'Groovy': [],
    
    # Functional Languages
    'Haskell': ['Functional Programming'],
    'F#': ['Functional Programming'],
    
    # Query Language
    'SQL': ['Database Querying'],
    
    # Markup/Data Formats
    'JSON': [],
    'XML': [],
    'YAML': [],
    
    # Notebooks
    'Jupyter Notebook': ['Data Analysis'],
}


# Framework to skills mapping with intelligent categorization
FRAMEWORK_SKILLS = {
    # Python Web Frameworks (names already in frameworks array, only add concept skills)
    'Django': ['RESTful APIs', 'ORM', 'MVC Architecture'],
    'Flask': ['RESTful APIs'],  # Removed: Microservices (can't determine architecture)
    'FastAPI': ['RESTful APIs', 'Async Programming', 'API Documentation'],
    
    # Python Data Science & ML (framework names in frameworks array)
    'TensorFlow': ['Machine Learning', 'Deep Learning', 'Neural Networks'],
    'PyTorch': ['Machine Learning', 'Deep Learning', 'Neural Networks'],
    'Keras': ['Machine Learning', 'Deep Learning', 'Neural Networks'],
    'Scikit-learn': ['Machine Learning', 'Statistical Modeling'],
    'Pandas': ['Data Analysis', 'Data Manipulation'],
    'NumPy': ['Numerical Computing', 'Scientific Computing'],
    'Streamlit': ['Data Visualization', 'Interactive Dashboards'],
    'Gradio': ['Machine Learning Interfaces', 'Interactive Demos'],
    
    # Python Tools
    'Celery': ['Task Queue Management', 'Asynchronous Processing'],
    'Scrapy': ['Web Scraping', 'Data Extraction'],
    'SQLAlchemy': ['ORM'],  # Removed: Database Management (redundant with ORM)
    'Pytest': ['Unit Testing', 'Test-Driven Development'],
    'Poetry': ['Dependency Management'],
    
    # JavaScript Frontend Frameworks (names in frameworks array)
    'React': ['Component-Based Architecture'],  # Removed: SPA (assumed), JSX (conditional)
    'Vue': ['Reactive UI'],  # Removed: PWA (assumed), SPA (assumed)
    'Angular': ['Dependency Injection', 'RxJS'],  # Removed: Enterprise Applications (too vague)
    'Svelte': ['Compiled Components', 'Reactive UI'],
    'Solid.js': ['Fine-Grained Reactivity'],  # Removed: Performance Optimization (assumed)
    'Preact': [],  # Lightweight alternative, no unique skills
    
    # Meta-Frameworks
    'Next.js': ['Server-Side Rendering', 'Static Site Generation'],
    'Nuxt.js': ['Server-Side Rendering'],
    'Gatsby': ['Static Site Generation', 'JAMstack', 'GraphQL'],
    'Remix': ['Nested Routing', 'Progressive Enhancement'],
    'Astro': ['Static Site Generation', 'Partial Hydration'],
    'SvelteKit': ['Server-Side Rendering'],
    
    # Backend JavaScript/Node.js
    'Express': ['RESTful APIs', 'Middleware'],
    'Koa': ['RESTful APIs', 'Async/Await'],
    'Fastify': ['High-Performance APIs', 'Schema Validation'],
    'Hapi': ['Enterprise APIs', 'Plugin Architecture'],
    'NestJS': ['Enterprise Architecture', 'Dependency Injection'],
    'Apollo Server': ['GraphQL Server', 'Schema Design'],
    
    # State Management
    'Redux': ['State Management', 'Predictable State Container'],
    'MobX': ['State Management', 'Observable State'],
    'Zustand': ['State Management'],
    'Recoil': ['State Management', 'Atomic State'],
    'Vuex': ['State Management'],
    'Pinia': ['State Management'],
    
    # UI Component Libraries (removed redundant "Component Libraries" and "Material Design")
    'Material-UI': [],  # Framework name in frameworks array
    'Ant Design': ['Enterprise UI'],
    'Chakra UI': ['Accessible Design', 'Design System'],
    'Semantic UI': ['Theming'],
    'Headless UI': ['Accessible Components'],
    'React Bootstrap': [],  # Just Bootstrap + React
    'Vuetify': [],  # Framework name in frameworks array
    'Mantine': [],  # Framework name in frameworks array
    
    # CSS Frameworks
    'Tailwind CSS': ['Utility-First CSS', 'Responsive Design'],
    'Bootstrap': ['Responsive Design', 'Grid System'],
    'Bulma': ['Responsive Design'],
    'Sass': ['CSS Preprocessing'],
    'Less': ['CSS Preprocessing'],
    'Emotion': ['CSS-in-JS'],
    'Styled Components': ['CSS-in-JS'],
    
    # Testing Frameworks
    'Jest': ['Unit Testing', 'Test-Driven Development'],
    'Vitest': ['Unit Testing'],
    'Mocha': ['Unit Testing', 'Test-Driven Development'],
    'Jasmine': ['Unit Testing', 'Behavior-Driven Development'],
    'Cypress': ['End-to-End Testing', 'Test Automation'],
    'Playwright': ['End-to-End Testing', 'Cross-Browser Testing'],
    'Testing Library': ['Component Testing', 'User-Centric Testing'],
    
    # Build Tools (removed redundant "Module Bundling")
    'Webpack': ['Build Optimization'],
    'Vite': [],  # Modern bundler, no unique skills
    'Rollup': [],  # Bundler, no unique skills
    'Parcel': [],  # Zero-config bundler, no unique skills
    'esbuild': [],  # Fast bundler, no unique skills
    'Turbopack': [],  # Next-gen bundler, no unique skills
    
    # GraphQL
    'GraphQL': ['GraphQL', 'API Design', 'Data Fetching'],
    'Apollo Client': ['GraphQL', 'State Management', 'Data Fetching'],
    'Relay': ['GraphQL', 'Data Management'],
    'URQL': ['GraphQL', 'Data Fetching'],
    
    # ORM & Database (removed redundant "Database Management" when ORM present)
    'Prisma': ['ORM'],
    'TypeORM': ['ORM'],
    'Sequelize': ['ORM'],
    'Mongoose': ['ODM', 'NoSQL'],
    'Drizzle ORM': ['ORM'],
    
    # Mobile Frameworks
    'React Native': ['Mobile Development', 'Cross-Platform Development'],
    'Expo': ['Mobile Development'],  # Removed: Rapid Prototyping (assumed)
    'Ionic': ['Hybrid Mobile Apps', 'Cross-Platform Development'],
    'NativeScript': ['Cross-Platform Development'],
    'Flutter': ['Mobile Development', 'Cross-Platform Development'],
    
    # Desktop Frameworks
    'Electron': ['Desktop Application Development', 'Cross-Platform Desktop'],
    'Tauri': ['Desktop Application Development'],
    
    # Java Frameworks
    'Spring Boot': ['Enterprise Java', 'Microservices', 'RESTful APIs'],
    'Spring': ['Enterprise Java', 'Dependency Injection'],
    'Hibernate': ['ORM', 'Java Persistence'],
    'JUnit': ['Unit Testing', 'Test-Driven Development'],
    'Mockito': ['Mocking', 'Unit Testing'],
    'Ktor': ['Asynchronous APIs'],
    
    # Ruby Frameworks
    'Rails': ['MVC Architecture', 'RESTful APIs', 'Convention over Configuration'],
    'Sinatra': ['Lightweight Web Apps'],
    'Hanami': [],  # Modern Ruby framework, no unique skills
    'RSpec': ['Behavior-Driven Development'],
    'Capybara': ['Integration Testing', 'Web Testing'],
    
    # PHP Frameworks
    'Laravel': ['MVC Architecture', 'Eloquent ORM'],
    'Symfony': ['Component-Based Architecture', 'Enterprise Development'],
    'CodeIgniter': [],  # Lightweight framework, no unique skills
    'CakePHP': ['Rapid Development'],
    'Yii': ['High-Performance Applications'],
    'Slim': [],  # Removed: Microservices (can't determine architecture)
    'PHPUnit': ['Unit Testing', 'Test-Driven Development'],
    
    # Go Frameworks
    'Gin': ['RESTful APIs', 'High-Performance Web'],
    'Echo': ['RESTful APIs'],
    'Fiber': ['High-Performance APIs'],
    'Beego': ['MVC Architecture'],  # Removed: Enterprise Applications (too vague)
    'Chi': ['RESTful APIs', 'HTTP Routing'],
    'Gorilla': ['HTTP Routing'],
    'GORM': ['ORM'],  # Removed: Database Management (redundant with ORM)
    
    # Rust Frameworks
    'Actix': ['High-Performance Web', 'Actor Model'],
    'Rocket': ['Type-Safe APIs'],
    'Axum': ['Async APIs'],
    'Warp': [],  # Functional web framework, no unique skills
    'Tokio': ['Async Programming', 'Concurrency'],
    'Serde': ['Serialization'],
    
    # .NET Frameworks
    'ASP.NET Core': ['Cross-Platform Web', 'Enterprise Development'],
    'Entity Framework': ['ORM'],  # Removed: Database Management (redundant with ORM)
    'Blazor': ['WebAssembly', 'Interactive Web'],
    'xUnit': ['Unit Testing', 'Test-Driven Development'],
    'NUnit': ['Unit Testing', 'Test-Driven Development'],
    
    # Other Libraries
    'Three.js': ['3D Graphics', 'WebGL', 'Interactive Visualization'],
    'D3.js': ['Data Visualization', 'Interactive Charts'],
    'Socket.IO': ['Real-Time Communication', 'WebSockets'],
    'Axios': [],  # HTTP client, removed "API Integration" (too generic)
    'Docker': ['Containerization'],  # Docker adds Containerization skill, not its own name
}


# File extension to skills mapping for specialized file types
FILE_TYPE_SKILLS = {
    # Design Files - Adobe Creative Suite
    '.psd': ['Adobe Photoshop', 'Photo Editing', 'Graphic Design', 'Digital Art'],
    '.ai': ['Adobe Illustrator', 'Vector Graphics', 'Graphic Design', 'Logo Design'],
    '.eps': ['Vector Graphics', 'Print Design', 'Adobe Illustrator'],
    
    # Design Files - Modern Tools
    '.sketch': ['Sketch', 'UI/UX Design', 'Interface Design', 'Prototyping'],
    '.fig': ['Figma', 'UI/UX Design', 'Collaborative Design', 'Prototyping'],
    
    # Photography - RAW Formats
    '.raw': ['Photography', 'RAW Photo Processing', 'Professional Photography'],
    '.cr2': ['Photography', 'Canon RAW Processing', 'Professional Photography'],
    '.nef': ['Photography', 'Nikon RAW Processing', 'Professional Photography'],
    '.arw': ['Photography', 'Sony RAW Processing', 'Professional Photography'],
    
    # Standard Image Formats (when in large quantities)
    '.jpg': ['Photography', 'Image Editing'],
    '.jpeg': ['Photography', 'Image Editing'],
    '.png': ['Image Editing', 'Digital Graphics'],
    '.webp': ['Modern Web Graphics', 'Image Optimization'],
    
    # Vector & Scalable Graphics
    '.svg': ['Vector Graphics', 'Scalable Design', 'Web Graphics'],
    
    # Video Files
    '.mp4': ['Video Editing', 'Multimedia Production'],
    '.avi': ['Video Editing', 'Multimedia Production'],
    '.mov': ['Video Editing', 'Multimedia Production'],
    '.wmv': ['Video Editing', 'Multimedia Production'],
    '.flv': ['Video Editing', 'Streaming Media'],
    '.webm': ['Web Video', 'Modern Video Formats'],
    
    # Audio Files
    '.mp3': ['Audio Editing', 'Music Production'],
    '.wav': ['Audio Editing', 'Professional Audio', 'Music Production'],
    '.flac': ['Audio Engineering', 'Lossless Audio', 'Music Production'],
    '.aac': ['Audio Editing', 'Audio Compression'],
    '.ogg': ['Audio Editing', 'Open-Source Audio'],
    
    # 3D & CAD
    '.blend': ['Blender', '3D Modeling', '3D Animation'],
    '.obj': ['3D Modeling', '3D Graphics'],
    '.fbx': ['3D Modeling', '3D Animation', 'Game Development'],
    '.stl': ['3D Modeling', '3D Printing', 'CAD'],
    '.dwg': ['AutoCAD', 'CAD', 'Technical Drawing'],
    
    # Documents & Technical Writing
    '.tex': ['LaTeX', 'Technical Writing', 'Document Preparation'],
    '.bib': ['Bibliography Management', 'Academic Writing', 'LaTeX'],
    '.md': ['Markdown', 'Documentation', 'Technical Writing'],
    '.rst': ['reStructuredText', 'Documentation', 'Python Documentation'],
    
    # Configuration & DevOps (framework names in frameworks array)
    '.dockerfile': ['Containerization'],
    '.dockerignore': ['Containerization'],
    'docker-compose.yml': ['Containerization', 'Multi-Container Applications'],
    '.gitlab-ci.yml': ['Continuous Integration', 'DevOps'],
    '.travis.yml': ['Continuous Integration', 'DevOps'],
    'jenkinsfile': ['CI/CD', 'Build Automation', 'DevOps'],  # lowercase for matching
    '.circleci/config.yml': ['Continuous Integration', 'DevOps'],
    
    # Database
    '.sql': ['SQL', 'Database Design', 'Query Optimization'],
    '.db': ['Database Management', 'SQLite'],
    '.sqlite': ['SQLite', 'Database Management'],
    
    # Jupyter & Data Science
    '.ipynb': ['Jupyter Notebooks', 'Data Analysis', 'Interactive Computing', 'Data Science'],
}


def extract_resume_skills(
    root_dir: Union[str, Path],
    languages: List[str] = None,
    frameworks: List[str] = None
) -> List[str]:
    """
    Extract comprehensive resume-ready skills from a project.
    
    Analyzes languages, frameworks, and file types to determine what professional
    skills are demonstrated in the project. This goes beyond simple detection to
    infer actual capabilities based on evidence.
    
    Args:
        root_dir: Path to the project directory
        languages: Optional pre-detected list of languages (will detect if not provided)
        frameworks: Optional pre-detected list of frameworks (will detect if not provided)
        
    Returns:
        Sorted list of unique skills, prioritized by relevance
        
    Example:
        >>> extract_resume_skills('/path/to/project')
        ['Backend Development', 'RESTful APIs', 'Containerization', 'Photo Editing']
    """
    from .project_metadata import detect_languages, detect_frameworks
    
    root_path = Path(root_dir)
    all_skills = set()
    
    # Get languages if not provided
    if languages is None:
        languages = detect_languages(root_path)
    
    # Get frameworks if not provided
    if frameworks is None:
        frameworks = detect_frameworks(root_path)
    
    # Extract skills from each source
    all_skills.update(extract_skills_from_languages(languages))
    all_skills.update(extract_skills_from_frameworks(frameworks))
    all_skills.update(extract_skills_from_files(root_path))
    
    # Cross-source inference: Add contextual skills based on language + framework combinations
    # This is where we infer skills like "Backend Development", "Frontend Development", etc.
    all_skills.update(_infer_contextual_skills(languages, frameworks))
    
    # Sort and return
    return sorted(list(all_skills))


def _infer_contextual_skills(languages: List[str], frameworks: List[str]) -> Set[str]:
    """
    Infer contextual skills based on language + framework combinations.
    
    Relaxed detection: Recognizes both modern framework-based apps and traditional
    web applications (e.g., Java + HTML/CSS for JSP apps, Python + HTML for Django templates).
    
    Args:
        languages: List of detected languages
        frameworks: List of detected frameworks
        
    Returns:
        Set of inferred contextual skills
    """
    skills = set()
    lang_set = set(languages)
    framework_set = set(frameworks)
    
    # Backend Development - Relaxed: backend language is sufficient
    # Can be with or without frameworks (traditional or modern)
    backend_langs = {'Python', 'Java', 'C#', 'Go', 'Rust', 'PHP', 'Ruby', 'Kotlin', 'Scala', 'Elixir', 'Erlang'}
    backend_frameworks = {'Django', 'Flask', 'FastAPI', 'Express', 'Koa', 'Fastify', 'Hapi', 
                         'NestJS', 'Spring Boot', 'Spring', 'Rails', 'Sinatra', 'Laravel', 
                         'Symfony', 'Gin', 'Echo', 'Fiber', 'Actix', 'Rocket', 'ASP.NET Core'}
    
    # Frontend Development - Relaxed: 
    # - Modern: JS/TS with frameworks (React, Vue, etc.)
    # - Traditional: HTML + CSS (static sites or server-rendered)
    frontend_langs = {'JavaScript', 'TypeScript'}
    frontend_frameworks = {'React', 'Vue', 'Angular', 'Svelte', 'Solid.js', 'Preact',
                          'Next.js', 'Nuxt.js', 'Gatsby', 'Remix', 'Astro', 'SvelteKit'}
    
    # Detect backend presence (language-based, more relaxed)
    has_backend = bool(lang_set & backend_langs)
    
    # Detect frontend presence (modern frameworks OR traditional HTML+CSS)
    has_modern_frontend = (lang_set & frontend_langs) and (framework_set & frontend_frameworks)
    has_traditional_frontend = ('HTML' in lang_set) or ('CSS' in lang_set)
    has_frontend = has_modern_frontend or has_traditional_frontend
    
    # Full-Stack Development - Relaxed: backend language + any frontend indication
    # This covers:
    # - Modern: Python + Django + React
    # - Traditional: Java + HTML/CSS (JSP), PHP + HTML/CSS, Python + Django templates
    if has_backend and has_frontend:
        skills.add('Full-Stack Development')
    else:
        # Only add Frontend or Backend if it's NOT a full-stack project
        if has_backend:
            skills.add('Backend Development')
        if has_modern_frontend:
            skills.add('Frontend Development')
        elif has_traditional_frontend and not has_backend:
            # Pure frontend (HTML/CSS only, no backend language)
            skills.add('Frontend Development')
    
    # Mobile Development - if mobile language + mobile framework
    mobile_frameworks = {'React Native', 'Expo', 'Ionic', 'NativeScript', 'Flutter'}
    
    if 'Swift' in lang_set:
        skills.add('Mobile Development')  # Swift is specifically for iOS
    
    if 'Dart' in lang_set and 'Flutter' in framework_set:
        skills.add('Mobile Development')
    
    if (lang_set & frontend_langs) and (framework_set & mobile_frameworks):
        skills.add('Mobile Development')
    
    # Data Science - if data science language + data frameworks
    if 'Python' in lang_set:
        data_frameworks = {'Pandas', 'NumPy', 'Scikit-learn', 'Jupyter Notebook'}
        if framework_set & data_frameworks:
            skills.add('Data Science')
    
    if 'R' in lang_set:
        skills.add('Data Science')  # R is specifically for data science
    
    # Machine Learning - if ML frameworks are present
    ml_frameworks = {'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn'}
    if framework_set & ml_frameworks:
        skills.add('Machine Learning')
    
    # DevOps - only if there's evidence of automation + infrastructure
    # Require BOTH containerization AND scripting to infer DevOps
    has_containers = 'Docker' in framework_set
    has_scripting = lang_set & {'Shell', 'PowerShell', 'Batch'}
    
    if has_containers and has_scripting:
        skills.add('DevOps')
    
    # Note: CI/CD tools (Jenkins, GitLab CI, etc.) will add DevOps via file detection
    
    return skills


def extract_skills_from_languages(languages: List[str]) -> Set[str]:
    """
    Extract skills from detected programming languages.
    
    Only includes skills that are directly demonstrated by the language itself.
    More complex skills (like "Full-Stack Development") are inferred from
    language + framework combinations in the main extract_skills function.
    
    Args:
        languages: List of detected programming languages
        
    Returns:
        Set of skills derived from the languages
    """
    skills = set()
    
    for language in languages:
        if language in LANGUAGE_SKILLS:
            skills.update(LANGUAGE_SKILLS[language])
    
    # Web Design skill when HTML + CSS are detected together
    if 'HTML' in languages and 'CSS' in languages:
        skills.add('Web Design')
    
    return skills


def extract_skills_from_frameworks(frameworks: List[str]) -> Set[str]:
    """
    Extract skills from detected frameworks and libraries.
    
    Only includes skills that are directly demonstrated by the framework itself.
    Broader contextual skills (like "Backend Development", "Full-Stack Development")
    are inferred in _infer_contextual_skills based on language + framework combinations.
    
    Args:
        frameworks: List of detected frameworks
        
    Returns:
        Set of skills derived from the frameworks
    """
    skills = set()
    
    # Add skills directly from framework mappings
    for framework in frameworks:
        if framework in FRAMEWORK_SKILLS:
            skills.update(FRAMEWORK_SKILLS[framework])
    
    # Add framework combination-based specializations
    # These are skills that only emerge from using MULTIPLE frameworks together
    framework_set = set(frameworks)
    
    # Machine Learning Engineering - using multiple ML frameworks shows ML engineering skill
    ml_frameworks = {'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn'}
    if len(framework_set & ml_frameworks) >= 2:
        skills.add('Machine Learning Engineering')
    
    # Testing Expertise - using multiple testing frameworks shows testing specialization
    test_frameworks = {'Jest', 'Pytest', 'Cypress', 'Playwright', 'JUnit', 'Vitest', 'Mocha', 'RSpec'}
    if len(framework_set & test_frameworks) >= 2:
        skills.add('Test Automation')
    
    return skills


def extract_skills_from_files(root_dir: Union[str, Path]) -> Set[str]:
    """
    Extract skills from file types, especially for creative and specialized work.
    
    This is particularly useful for detecting skills like photography, graphic design,
    video editing, and other non-coding skills demonstrated in a project.
    
    Args:
        root_dir: Path to the project directory
        
    Returns:
        Set of skills derived from file types
    """
    root_path = Path(root_dir)
    skills = set()
    file_counter = Counter()
    
    # Walk through directory and count file types
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip common ignored directories
        skip_dirs = {'.git', 'node_modules', 'venv', '.venv', '__pycache__', 'build', 'dist'}
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            
            # Also check for special filenames without extensions
            if filename.lower() in FILE_TYPE_SKILLS:
                skills.update(FILE_TYPE_SKILLS[filename.lower()])
            
            if ext in FILE_TYPE_SKILLS:
                file_counter[ext] += 1
    
    # Add skills based on file type counts with thresholds
    # This prevents adding "Photography" for a single logo file
    
    # Photography skills (require multiple files)
    photo_raw_exts = {'.raw', '.cr2', '.nef', '.arw'}
    photo_count = sum(file_counter[ext] for ext in photo_raw_exts if ext in file_counter)
    if photo_count >= 3:
        skills.add('Photography')
        skills.add('RAW Photo Processing')
    
    standard_photo_exts = {'.jpg', '.jpeg'}
    standard_photo_count = sum(file_counter[ext] for ext in standard_photo_exts if ext in file_counter)
    if standard_photo_count >= 10:
        skills.add('Photography')
    
    # Design skills
    if file_counter.get('.psd', 0) >= 1:
        skills.update(FILE_TYPE_SKILLS['.psd'])
    
    if file_counter.get('.ai', 0) >= 1:
        skills.update(FILE_TYPE_SKILLS['.ai'])
    
    if file_counter.get('.sketch', 0) >= 1:
        skills.update(FILE_TYPE_SKILLS['.sketch'])
    
    if file_counter.get('.fig', 0) >= 1:
        skills.update(FILE_TYPE_SKILLS['.fig'])
    
    # Video editing (require multiple files)
    video_exts = {'.mp4', '.avi', '.mov', '.wmv'}
    video_count = sum(file_counter[ext] for ext in video_exts if ext in file_counter)
    if video_count >= 2:
        skills.add('Video Editing')
        skills.add('Multimedia Production')
    
    # Audio production (require multiple files)
    audio_exts = {'.wav', '.flac', '.aac'}
    audio_count = sum(file_counter[ext] for ext in audio_exts if ext in file_counter)
    if audio_count >= 3:
        skills.add('Audio Editing')
        skills.add('Music Production')
    
    # 3D modeling
    modeling_exts = {'.blend', '.obj', '.fbx', '.stl'}
    if any(file_counter.get(ext, 0) >= 1 for ext in modeling_exts):
        skills.add('3D Modeling')
    
    # Technical writing
    if file_counter.get('.tex', 0) >= 1:
        skills.update(FILE_TYPE_SKILLS['.tex'])
    
    if file_counter.get('.md', 0) >= 5:
        skills.add('Documentation')
        skills.add('Technical Writing')
    
    # Data Science indicators
    if file_counter.get('.ipynb', 0) >= 1:
        skills.update(FILE_TYPE_SKILLS['.ipynb'])
    
    return skills


def get_skill_categories() -> dict:
    """
    Return a categorized view of all possible skills.
    
    Returns:
        Dictionary mapping skill categories to lists of skills
    """
    categories = {
        'Programming Languages': set(),
        'Web Development': set(),
        'Mobile Development': set(),
        'Data Science & ML': set(),
        'Design & Creative': set(),
        'DevOps & Infrastructure': set(),
        'Testing & QA': set(),
        'Database & ORM': set(),
        'Other': set(),
    }
    
    # Categorize language skills
    for skills in LANGUAGE_SKILLS.values():
        for skill in skills:
            if any(keyword in skill for keyword in ['Programming', 'Development', 'Scripting']):
                categories['Programming Languages'].add(skill)
    
    # Categorize framework skills
    for skills in FRAMEWORK_SKILLS.values():
        for skill in skills:
            if any(keyword in skill for keyword in ['Machine Learning', 'Data Science', 'AI', 'Deep Learning']):
                categories['Data Science & ML'].add(skill)
            elif any(keyword in skill for keyword in ['Mobile', 'iOS', 'Android']):
                categories['Mobile Development'].add(skill)
            elif any(keyword in skill for keyword in ['Testing', 'Test-Driven', 'QA', 'Quality']):
                categories['Testing & QA'].add(skill)
            elif any(keyword in skill for keyword in ['DevOps', 'Docker', 'CI/CD', 'Container']):
                categories['DevOps & Infrastructure'].add(skill)
            elif any(keyword in skill for keyword in ['ORM', 'Database', 'SQL']):
                categories['Database & ORM'].add(skill)
            elif any(keyword in skill for keyword in ['Frontend', 'Backend', 'Web', 'API']):
                categories['Web Development'].add(skill)
    
    # Categorize file type skills
    for skills in FILE_TYPE_SKILLS.values():
        for skill in skills:
            if any(keyword in skill for keyword in ['Design', 'Photo', 'Video', 'Audio', '3D', 'Graphics']):
                categories['Design & Creative'].add(skill)
    
    return {k: sorted(list(v)) for k, v in categories.items() if v}

