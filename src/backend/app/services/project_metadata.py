"""
Project Metadata Detection Module

This module provides functionality to detect programming languages and frameworks
used in software projects. It can be used independently or as part of the project
classification pipeline.

Main functions:
    - detect_languages(): Detect programming languages used in a project
    - detect_frameworks(): Detect frameworks and libraries used in a project
"""

import os
import json
import re
from pathlib import Path
from collections import Counter
from typing import List, Union


# Extension to language mapping for language detection
EXTENSION_TO_LANGUAGE = {
    # Python
    '.py': 'Python',
    '.pyw': 'Python',
    '.pyi': 'Python',
    
    # JavaScript
    '.js': 'JavaScript',
    '.jsx': 'JavaScript',
    '.mjs': 'JavaScript',
    '.cjs': 'JavaScript',
    
    # TypeScript
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    
    # Java
    '.java': 'Java',
    '.jsp': 'Java',
    
    # C/C++
    '.c': 'C',
    '.h': 'C',
    '.cpp': 'C++',
    '.cc': 'C++',
    '.cxx': 'C++',
    '.hpp': 'C++',
    '.hh': 'C++',
    
    # C#
    '.cs': 'C#',
    
    # Go
    '.go': 'Go',
    
    # Rust
    '.rs': 'Rust',
    
    # PHP
    '.php': 'PHP',
    '.php3': 'PHP',
    '.php4': 'PHP',
    '.php5': 'PHP',
    '.phtml': 'PHP',
    
    # Ruby
    '.rb': 'Ruby',
    
    # Swift
    '.swift': 'Swift',
    
    # Kotlin
    '.kt': 'Kotlin',
    '.kts': 'Kotlin',
    
    # Scala
    '.scala': 'Scala',
    '.sc': 'Scala',
    
    # Shell
    '.sh': 'Shell',
    '.bash': 'Shell',
    '.zsh': 'Shell',
    
    # PowerShell
    '.ps1': 'PowerShell',
    '.psm1': 'PowerShell',
    
    # Batch
    '.bat': 'Batch',
    '.cmd': 'Batch',
    
    # Perl
    '.pl': 'Perl',
    '.pm': 'Perl',
    
    # R
    '.r': 'R',
    
    # Julia
    '.jl': 'Julia',
    
    # Haskell
    '.hs': 'Haskell',
    '.lhs': 'Haskell',
    
    # Erlang
    '.erl': 'Erlang',
    
    # Elixir
    '.ex': 'Elixir',
    '.exs': 'Elixir',
    
    # F#
    '.fs': 'F#',
    '.fsi': 'F#',
    
    # Visual Basic
    '.vb': 'Visual Basic',
    
    # SQL
    '.sql': 'SQL',
    
    # Assembly
    '.asm': 'Assembly',
    '.s': 'Assembly',
    
    # Groovy
    '.groovy': 'Groovy',
    
    # Dart
    '.dart': 'Dart',
    
    # Lua
    '.lua': 'Lua',
    
    # Web
    '.html': 'HTML',
    '.htm': 'HTML',
    '.css': 'CSS',
    
    # Jupyter
    '.ipynb': 'Jupyter Notebook',
    
    # XML (for configuration, not really a programming language but useful)
    '.xml': 'XML',
    
    # Note: The following extensions from CODE_EXTS are intentionally NOT mapped:
    # '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'
    # These are data/configuration formats, not programming languages.
    # They are useful for classification but don't represent a programming language.
}


def detect_languages(root_dir: Union[str, Path]) -> List[str]:
    """
    Detect programming languages used in a project.
    
    Analyzes file extensions in the project directory to determine which
    programming languages are used. Languages are returned in order of
    prevalence (most files first).
    
    Args:
        root_dir: Path to the project directory
        
    Returns:
        List of detected languages, sorted by prevalence (most used first)
        
    Example:
        >>> detect_languages('/path/to/project')
        ['Python', 'JavaScript', 'HTML', 'CSS']
    """
    root_path = Path(root_dir)
    language_counts = Counter()
    
    # Walk through the directory and count language files
    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in EXTENSION_TO_LANGUAGE:
                language = EXTENSION_TO_LANGUAGE[ext]
                language_counts[language] += 1
    
    # Return languages sorted by count (most common first)
    return [lang for lang, count in language_counts.most_common()]


def detect_frameworks(root_dir: Union[str, Path]) -> List[str]:
    """
    Detect frameworks and libraries used in a project.
    
    Comprehensively analyzes dependency files (requirements.txt, package.json, 
    Pipfile, pyproject.toml, Gemfile, etc.), configuration files, and source code 
    to detect which frameworks are being used in the project.
    
    Args:
        root_dir: Path to the project directory
        
    Returns:
        Sorted list of detected frameworks
        
    Example:
        >>> detect_frameworks('/path/to/project')
        ['Django', 'React', 'TensorFlow', 'Jest', 'Webpack']
    """
    root_path = Path(root_dir)
    frameworks = set()
    
    # Walk through the directory and check for framework indicators
    for dirpath, dirnames, filenames in os.walk(root_path):
        dir_path = Path(dirpath)
        
        for filename in filenames:
            file_path = dir_path / filename
            
            # Python dependency files
            if filename == 'requirements.txt':
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    frameworks.update(_detect_python_frameworks_from_requirements(content))
                except Exception:
                    pass
            
            elif filename == 'Pipfile':
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    frameworks.update(_detect_python_frameworks_from_pipfile(content))
                except Exception:
                    pass
            
            elif filename == 'pyproject.toml':
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    frameworks.update(_detect_python_frameworks_from_pyproject(content))
                except Exception:
                    pass
            
            elif filename == 'setup.py':
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    frameworks.update(_detect_python_frameworks_from_setup(content))
                except Exception:
                    pass
            
            elif filename == 'manage.py':
                # Django indicator
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    if 'django' in content.lower():
                        frameworks.add('Django')
                except Exception:
                    pass
            
            # Node.js dependency files
            elif filename == 'package.json':
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    frameworks.update(_detect_js_frameworks_from_package_json(content))
                except Exception:
                    pass
            
            elif filename == 'package-lock.json':
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    frameworks.update(_detect_js_frameworks_from_package_lock(content))
                except Exception:
                    pass
            
            elif filename == 'yarn.lock':
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    frameworks.update(_detect_js_frameworks_from_yarn_lock(content))
                except Exception:
                    pass
            
            # Node.js configuration files
            elif filename == 'next.config.js' or filename == 'next.config.ts':
                frameworks.add('Next.js')
            
            elif filename == 'angular.json':
                frameworks.add('Angular')
            
            elif filename == 'nuxt.config.js' or filename == 'nuxt.config.ts':
                frameworks.add('Nuxt.js')
            
            elif filename == 'gatsby-config.js':
                frameworks.add('Gatsby')
            
            elif filename == 'svelte.config.js':
                frameworks.add('Svelte')
            
            elif filename == 'vite.config.js' or filename == 'vite.config.ts':
                frameworks.add('Vite')
            
            elif filename == 'webpack.config.js':
                frameworks.add('Webpack')
            
            elif filename == 'tailwind.config.js':
                frameworks.add('Tailwind CSS')
            
            # Java dependency files
            elif filename == 'pom.xml':
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    frameworks.update(_detect_java_frameworks_from_pom(content))
                except Exception:
                    pass
            
            elif filename == 'build.gradle' or filename == 'build.gradle.kts':
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    frameworks.update(_detect_java_frameworks_from_gradle(content))
                except Exception:
                    pass
            
            # Ruby dependency files
            elif filename == 'Gemfile':
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    frameworks.update(_detect_ruby_frameworks_from_gemfile(content))
                except Exception:
                    pass
            
            # PHP dependency files
            elif filename == 'composer.json':
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    frameworks.update(_detect_php_frameworks_from_composer(content))
                except Exception:
                    pass
            
            elif filename == 'artisan':
                frameworks.add('Laravel')
            
            # Go dependency files
            elif filename == 'go.mod':
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    frameworks.update(_detect_go_frameworks_from_mod(content))
                except Exception:
                    pass
            
            # Rust dependency files
            elif filename == 'Cargo.toml':
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    frameworks.update(_detect_rust_frameworks_from_cargo(content))
                except Exception:
                    pass
            
            # .NET files
            elif filename.endswith('.csproj'):
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    frameworks.update(_detect_dotnet_frameworks_from_csproj(content))
                except Exception:
                    pass
            
            # Docker files (container orchestration)
            elif filename == 'Dockerfile' or filename == 'docker-compose.yml':
                frameworks.add('Docker')
            
            # Check Python files for framework imports (limit to avoid scanning too many files)
            elif filename.endswith('.py') and _should_scan_for_imports(file_path):
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    frameworks.update(_detect_frameworks_from_python_imports(content))
                except Exception:
                    pass
            
            # Check for Vue files
            elif filename.endswith('.vue'):
                frameworks.add('Vue')
            
            # Check for Svelte files
            elif filename.endswith('.svelte'):
                frameworks.add('Svelte')
    
    return sorted(list(frameworks))


# Helper functions for framework detection

def _should_scan_for_imports(file_path: Path) -> bool:
    """
    Determine if a Python file should be scanned for imports.
    Avoid scanning very large files or files in certain directories.
    """
    try:
        # Skip files larger than 100KB
        if file_path.stat().st_size > 100_000:
            return False
        
        # Skip files in common large directories
        path_str = str(file_path).lower()
        skip_dirs = ['node_modules', 'venv', '.venv', 'env', 'site-packages', '__pycache__', '.git']
        if any(skip_dir in path_str for skip_dir in skip_dirs):
            return False
        
        return True
    except Exception:
        return False


def _detect_python_frameworks_from_requirements(content: str) -> set:
    """
    Detect Python frameworks from requirements.txt content.
    
    Args:
        content: Contents of requirements.txt file
        
    Returns:
        Set of detected framework names
    """
    frameworks = set()
    
    # Define framework patterns - comprehensive list
    framework_patterns = {
        'Django': ['django==', 'django>=', 'django~=', 'django<', 'django>', 'django '],
        'Flask': ['flask==', 'flask>=', 'flask~=', 'flask<', 'flask>', 'flask '],
        'FastAPI': ['fastapi==', 'fastapi>=', 'fastapi~=', 'fastapi<', 'fastapi>', 'fastapi '],
        'TensorFlow': ['tensorflow==', 'tensorflow>=', 'tensorflow~=', 'tensorflow<', 'tensorflow>', 'tensorflow '],
        'PyTorch': ['torch==', 'torch>=', 'torch~=', 'torch<', 'torch>', 'torch '],
        'Pandas': ['pandas==', 'pandas>=', 'pandas~=', 'pandas<', 'pandas>', 'pandas '],
        'NumPy': ['numpy==', 'numpy>=', 'numpy~=', 'numpy<', 'numpy>', 'numpy '],
        'Scikit-learn': ['scikit-learn==', 'scikit-learn>=', 'sklearn'],
        'Keras': ['keras==', 'keras>=', 'keras~='],
        'Celery': ['celery==', 'celery>=', 'celery~='],
        'Scrapy': ['scrapy==', 'scrapy>=', 'scrapy~='],
        'Pytest': ['pytest==', 'pytest>=', 'pytest~='],
        'SQLAlchemy': ['sqlalchemy==', 'sqlalchemy>=', 'sqlalchemy~='],
        'Streamlit': ['streamlit==', 'streamlit>=', 'streamlit~='],
        'Gradio': ['gradio==', 'gradio>=', 'gradio~='],
    }
    
    content_lower = content.lower()
    for framework, patterns in framework_patterns.items():
        if any(pattern in content_lower for pattern in patterns):
            frameworks.add(framework)
    
    return frameworks


def _detect_python_frameworks_from_pipfile(content: str) -> set:
    """Detect Python frameworks from Pipfile content."""
    frameworks = set()
    content_lower = content.lower()
    
    framework_keywords = {
        'Django': 'django',
        'Flask': 'flask',
        'FastAPI': 'fastapi',
        'TensorFlow': 'tensorflow',
        'PyTorch': 'torch',
        'Pandas': 'pandas',
        'NumPy': 'numpy',
        'Scikit-learn': 'scikit-learn',
        'Celery': 'celery',
        'Scrapy': 'scrapy',
    }
    
    for framework, keyword in framework_keywords.items():
        if keyword in content_lower:
            frameworks.add(framework)
    
    return frameworks


def _detect_python_frameworks_from_pyproject(content: str) -> set:
    """Detect Python frameworks from pyproject.toml content."""
    frameworks = set()
    content_lower = content.lower()
    
    framework_keywords = {
        'Django': 'django',
        'Flask': 'flask',
        'FastAPI': 'fastapi',
        'TensorFlow': 'tensorflow',
        'PyTorch': 'torch',
        'Pandas': 'pandas',
        'NumPy': 'numpy',
        'Pytest': 'pytest',
        'Poetry': 'poetry',
    }
    
    for framework, keyword in framework_keywords.items():
        if keyword in content_lower:
            frameworks.add(framework)
    
    return frameworks


def _detect_python_frameworks_from_setup(content: str) -> set:
    """Detect Python frameworks from setup.py content."""
    frameworks = set()
    content_lower = content.lower()
    
    framework_keywords = {
        'Django': 'django',
        'Flask': 'flask',
        'FastAPI': 'fastapi',
        'TensorFlow': 'tensorflow',
        'PyTorch': 'torch',
    }
    
    for framework, keyword in framework_keywords.items():
        if keyword in content_lower:
            frameworks.add(framework)
    
    return frameworks


def _detect_js_frameworks_from_package_json(content: str) -> set:
    """
    Detect JavaScript frameworks from package.json content.
    Comprehensive detection of frameworks, libraries, and tools.
    
    Args:
        content: Contents of package.json file
        
    Returns:
        Set of detected framework names
    """
    frameworks = set()
    
    try:
        data = json.loads(content)
        dependencies = {}
        
        # Merge all dependency sections
        if 'dependencies' in data:
            dependencies.update(data['dependencies'])
        if 'devDependencies' in data:
            dependencies.update(data['devDependencies'])
        if 'peerDependencies' in data:
            dependencies.update(data['peerDependencies'])
        
        # Frontend frameworks
        if 'react' in dependencies or 'react-dom' in dependencies:
            frameworks.add('React')
        if 'vue' in dependencies:
            frameworks.add('Vue')
        if '@angular/core' in dependencies:
            frameworks.add('Angular')
        if 'svelte' in dependencies:
            frameworks.add('Svelte')
        if 'solid-js' in dependencies:
            frameworks.add('Solid.js')
        if 'preact' in dependencies:
            frameworks.add('Preact')
        
        # Meta-frameworks
        if 'next' in dependencies:
            frameworks.add('Next.js')
        if 'nuxt' in dependencies or 'nuxt3' in dependencies:
            frameworks.add('Nuxt.js')
        if 'gatsby' in dependencies:
            frameworks.add('Gatsby')
        if '@remix-run/react' in dependencies:
            frameworks.add('Remix')
        if 'astro' in dependencies:
            frameworks.add('Astro')
        if 'sveltekit' in dependencies or '@sveltejs/kit' in dependencies:
            frameworks.add('SvelteKit')
        
        # Backend frameworks
        if 'express' in dependencies:
            frameworks.add('Express')
        if 'koa' in dependencies:
            frameworks.add('Koa')
        if 'fastify' in dependencies:
            frameworks.add('Fastify')
        if 'hapi' in dependencies or '@hapi/hapi' in dependencies:
            frameworks.add('Hapi')
        if 'nestjs' in dependencies or '@nestjs/core' in dependencies:
            frameworks.add('NestJS')
        if 'apollo-server' in dependencies:
            frameworks.add('Apollo Server')
        
        # State management
        if 'redux' in dependencies or '@reduxjs/toolkit' in dependencies:
            frameworks.add('Redux')
        if 'mobx' in dependencies:
            frameworks.add('MobX')
        if 'zustand' in dependencies:
            frameworks.add('Zustand')
        if 'recoil' in dependencies:
            frameworks.add('Recoil')
        if 'vuex' in dependencies:
            frameworks.add('Vuex')
        if 'pinia' in dependencies:
            frameworks.add('Pinia')
        
        # UI libraries
        if '@mui/material' in dependencies or '@material-ui/core' in dependencies:
            frameworks.add('Material-UI')
        if 'antd' in dependencies:
            frameworks.add('Ant Design')
        if '@chakra-ui/react' in dependencies:
            frameworks.add('Chakra UI')
        if 'semantic-ui-react' in dependencies:
            frameworks.add('Semantic UI')
        if '@headlessui/react' in dependencies or '@headlessui/vue' in dependencies:
            frameworks.add('Headless UI')
        if 'react-bootstrap' in dependencies:
            frameworks.add('React Bootstrap')
        if 'vuetify' in dependencies:
            frameworks.add('Vuetify')
        if '@mantine/core' in dependencies:
            frameworks.add('Mantine')
        
        # CSS frameworks
        if 'tailwindcss' in dependencies:
            frameworks.add('Tailwind CSS')
        if 'bootstrap' in dependencies:
            frameworks.add('Bootstrap')
        if 'bulma' in dependencies:
            frameworks.add('Bulma')
        if '@emotion/react' in dependencies:
            frameworks.add('Emotion')
        if 'styled-components' in dependencies:
            frameworks.add('Styled Components')
        if 'sass' in dependencies or 'node-sass' in dependencies:
            frameworks.add('Sass')
        if 'less' in dependencies:
            frameworks.add('Less')
        
        # Testing frameworks
        if 'jest' in dependencies:
            frameworks.add('Jest')
        if 'vitest' in dependencies:
            frameworks.add('Vitest')
        if 'mocha' in dependencies:
            frameworks.add('Mocha')
        if 'jasmine' in dependencies or 'jasmine-core' in dependencies:
            frameworks.add('Jasmine')
        if 'cypress' in dependencies:
            frameworks.add('Cypress')
        if '@playwright/test' in dependencies:
            frameworks.add('Playwright')
        if '@testing-library/react' in dependencies or '@testing-library/vue' in dependencies:
            frameworks.add('Testing Library')
        
        # Build tools
        if 'webpack' in dependencies:
            frameworks.add('Webpack')
        if 'vite' in dependencies:
            frameworks.add('Vite')
        if 'rollup' in dependencies:
            frameworks.add('Rollup')
        if 'parcel' in dependencies or 'parcel-bundler' in dependencies:
            frameworks.add('Parcel')
        if 'esbuild' in dependencies:
            frameworks.add('esbuild')
        if 'turbopack' in dependencies:
            frameworks.add('Turbopack')
        
        # GraphQL
        if 'graphql' in dependencies:
            frameworks.add('GraphQL')
        if 'apollo-client' in dependencies or '@apollo/client' in dependencies:
            frameworks.add('Apollo Client')
        if 'relay-runtime' in dependencies:
            frameworks.add('Relay')
        if 'urql' in dependencies:
            frameworks.add('URQL')
        
        # ORM/Database
        if 'prisma' in dependencies or '@prisma/client' in dependencies:
            frameworks.add('Prisma')
        if 'typeorm' in dependencies:
            frameworks.add('TypeORM')
        if 'sequelize' in dependencies:
            frameworks.add('Sequelize')
        if 'mongoose' in dependencies:
            frameworks.add('Mongoose')
        if 'drizzle-orm' in dependencies:
            frameworks.add('Drizzle ORM')
        
        # Mobile frameworks
        if 'react-native' in dependencies:
            frameworks.add('React Native')
        if 'expo' in dependencies:
            frameworks.add('Expo')
        if '@ionic/react' in dependencies or '@ionic/vue' in dependencies or '@ionic/angular' in dependencies:
            frameworks.add('Ionic')
        if 'nativescript' in dependencies:
            frameworks.add('NativeScript')
        
        # Desktop frameworks
        if 'electron' in dependencies:
            frameworks.add('Electron')
        if 'tauri' in dependencies or '@tauri-apps/api' in dependencies:
            frameworks.add('Tauri')
        
        # Others
        if 'three' in dependencies:
            frameworks.add('Three.js')
        if 'd3' in dependencies:
            frameworks.add('D3.js')
        if 'socket.io' in dependencies:
            frameworks.add('Socket.IO')
        if 'axios' in dependencies:
            frameworks.add('Axios')
        
    except json.JSONDecodeError:
        pass
    
    return frameworks


def _detect_js_frameworks_from_package_lock(content: str) -> set:
    """Detect JavaScript frameworks from package-lock.json (fallback method)."""
    frameworks = set()
    content_lower = content.lower()
    
    # Simple keyword matching as fallback
    framework_keywords = {
        'React': '"react"',
        'Vue': '"vue"',
        'Angular': '"@angular/core"',
        'Express': '"express"',
        'Next.js': '"next"',
        'Jest': '"jest"',
        'Webpack': '"webpack"',
    }
    
    for framework, keyword in framework_keywords.items():
        if keyword in content_lower:
            frameworks.add(framework)
    
    return frameworks


def _detect_js_frameworks_from_yarn_lock(content: str) -> set:
    """Detect JavaScript frameworks from yarn.lock (fallback method)."""
    frameworks = set()
    
    # Simple keyword matching
    framework_keywords = {
        'React': 'react@',
        'Vue': 'vue@',
        'Angular': '@angular/core@',
        'Express': 'express@',
        'Next.js': 'next@',
    }
    
    for framework, keyword in framework_keywords.items():
        if keyword in content:
            frameworks.add(framework)
    
    return frameworks


def _detect_java_frameworks_from_pom(content: str) -> set:
    """Detect Java frameworks from pom.xml content."""
    frameworks = set()
    content_lower = content.lower()
    
    if 'springframework' in content_lower:
        if 'spring-boot' in content_lower:
            frameworks.add('Spring Boot')
        else:
            frameworks.add('Spring')
    
    if 'hibernate' in content_lower:
        frameworks.add('Hibernate')
    
    if 'junit' in content_lower:
        frameworks.add('JUnit')
    
    if 'mockito' in content_lower:
        frameworks.add('Mockito')
    
    return frameworks


def _detect_java_frameworks_from_gradle(content: str) -> set:
    """Detect Java frameworks from build.gradle content."""
    frameworks = set()
    content_lower = content.lower()
    
    framework_keywords = {
        'Spring Boot': 'org.springframework.boot',
        'Spring': 'springframework',
        'Hibernate': 'hibernate',
        'JUnit': 'junit',
        'Mockito': 'mockito',
        'Ktor': 'io.ktor',
    }
    
    for framework, keyword in framework_keywords.items():
        if keyword in content_lower:
            frameworks.add(framework)
    
    return frameworks


def _detect_ruby_frameworks_from_gemfile(content: str) -> set:
    """Detect Ruby frameworks from Gemfile content."""
    frameworks = set()
    content_lower = content.lower()
    
    framework_keywords = {
        'Rails': 'rails',
        'Sinatra': 'sinatra',
        'Hanami': 'hanami',
        'RSpec': 'rspec',
        'Capybara': 'capybara',
    }
    
    for framework, keyword in framework_keywords.items():
        if keyword in content_lower:
            frameworks.add(framework)
    
    return frameworks


def _detect_php_frameworks_from_composer(content: str) -> set:
    """Detect PHP frameworks from composer.json content."""
    frameworks = set()
    
    try:
        data = json.loads(content)
        require = data.get('require', {})
        require_dev = data.get('require-dev', {})
        all_requirements = {**require, **require_dev}
        
        framework_keywords = {
            'Laravel': 'laravel/framework',
            'Symfony': 'symfony/',
            'CodeIgniter': 'codeigniter/framework',
            'CakePHP': 'cakephp/cakephp',
            'Yii': 'yiisoft/yii2',
            'Slim': 'slim/slim',
            'PHPUnit': 'phpunit/phpunit',
        }
        
        for framework, keyword in framework_keywords.items():
            if any(keyword in req for req in all_requirements.keys()):
                frameworks.add(framework)
        
    except json.JSONDecodeError:
        pass
    
    return frameworks


def _detect_go_frameworks_from_mod(content: str) -> set:
    """Detect Go frameworks from go.mod content."""
    frameworks = set()
    content_lower = content.lower()
    
    framework_keywords = {
        'Gin': 'github.com/gin-gonic/gin',
        'Echo': 'github.com/labstack/echo',
        'Fiber': 'github.com/gofiber/fiber',
        'Beego': 'github.com/beego/beego',
        'Chi': 'github.com/go-chi/chi',
        'Gorilla': 'github.com/gorilla/',
        'GORM': 'gorm.io/gorm',
    }
    
    for framework, keyword in framework_keywords.items():
        if keyword.lower() in content_lower:
            frameworks.add(framework)
    
    return frameworks


def _detect_rust_frameworks_from_cargo(content: str) -> set:
    """Detect Rust frameworks from Cargo.toml content."""
    frameworks = set()
    content_lower = content.lower()
    
    framework_keywords = {
        'Actix': 'actix',
        'Rocket': 'rocket',
        'Axum': 'axum',
        'Warp': 'warp',
        'Tokio': 'tokio',
        'Serde': 'serde',
    }
    
    for framework, keyword in framework_keywords.items():
        if keyword in content_lower:
            frameworks.add(framework)
    
    return frameworks


def _detect_dotnet_frameworks_from_csproj(content: str) -> set:
    """Detect .NET frameworks from .csproj content."""
    frameworks = set()
    content_lower = content.lower()
    
    framework_keywords = {
        'ASP.NET Core': 'microsoft.aspnetcore',
        'Entity Framework': 'entityframework',
        'Blazor': 'blazor',
        'xUnit': 'xunit',
        'NUnit': 'nunit',
    }
    
    for framework, keyword in framework_keywords.items():
        if keyword in content_lower:
            frameworks.add(framework)
    
    return frameworks


def _detect_frameworks_from_python_imports(content: str) -> set:
    """
    Detect frameworks from Python import statements.
    Only scans smaller files to avoid performance issues.
    
    Args:
        content: Contents of a Python file
        
    Returns:
        Set of detected framework names
    """
    frameworks = set()
    
    # Look for common import patterns (case-insensitive)
    import_patterns = {
        'Flask': r'from\s+flask\s+import|import\s+flask\b',
        'FastAPI': r'from\s+fastapi\s+import|import\s+fastapi\b',
        'Django': r'from\s+django|import\s+django\b',
        'TensorFlow': r'import\s+tensorflow|import\s+tf\b',
        'PyTorch': r'import\s+torch\b',
        'Pandas': r'import\s+pandas|import\s+pd\b',
        'NumPy': r'import\s+numpy|import\s+np\b',
        'Scikit-learn': r'from\s+sklearn|import\s+sklearn',
        'Keras': r'from\s+keras|import\s+keras',
        'Streamlit': r'import\s+streamlit|import\s+st\b',
        'Gradio': r'import\s+gradio|import\s+gr\b',
    }
    
    for framework, pattern in import_patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            frameworks.add(framework)
    
    return frameworks

