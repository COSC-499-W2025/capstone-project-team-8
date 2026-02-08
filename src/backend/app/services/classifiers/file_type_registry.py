"""
File Type Registry Module

This module contains constants and utilities for classifying files by type.
Includes extension sets for different file categories and helper functions.
"""
import os
from typing import Set


# Extension sets for different file types
CODE_EXTS: Set[str] = {
    '.py', '.pyw', '.pyi',
    '.js', '.jsx', '.mjs', '.cjs',
    '.ts', '.tsx',
    '.java', '.jsp',
    '.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hh',
    '.cs',
    '.go',
    '.rs',
    '.php', '.php3', '.php4', '.php5', '.phtml',
    '.rb',
    '.swift',
    '.kt', '.kts',
    '.scala', '.sc',
    '.sh', '.bash', '.zsh',
    '.ps1', '.psm1', '.bat', '.cmd',
    '.pl', '.pm',
    '.r',
    '.jl',
    '.hs', '.lhs',
    '.erl', '.ex', '.exs',
    '.fs', '.fsi',
    '.vb',
    '.sql',
    '.asm', '.s',
    '.groovy',
    '.dart',
    '.lua',
    '.html', '.htm', '.css',
    '.json', '.xml',
    '.ipynb',  # Jupyter notebooks
    '.yaml', '.yml',  # Configuration files
    '.toml', '.ini', '.cfg', '.conf'
}

TEXT_EXTS: Set[str] = {
    '.txt', '.md', '.doc', '.docx', '.pdf', '.tex', '.bib',
    '.rtf', '.odt', '.pages',  # Additional document formats
    '.log'  # Log files
}

IMAGE_EXTS: Set[str] = {
    '.png', '.jpg', '.jpeg', '.svg', '.psd', '.gif', '.tiff', '.tif',
    '.bmp', '.webp', '.ico', '.raw', '.cr2', '.nef', '.arw',  # Additional image formats
    '.ai', '.eps', '.sketch', '.fig'  # Design files
}

OTHER_BINARY_EXTS: Set[str] = {
    '.exe', '.bin', '.dll', '.zip', '.tar', '.gz', '.7z', '.rar',
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',  # Video files
    '.mp3', '.wav', '.flac', '.aac', '.ogg',  # Audio files
    '.db', '.sqlite', '.sqlite3'  # Database files
}

# Folder name hints for different project types
FOLDER_HINTS = {
    'code': {
        'src', 'lib', 'bin', 'app', 'srcs', 'source', 'sources',
        'code', 'scripts', 'utils', 'helpers', 'core', 'modules',
        'components', 'services', 'controllers', 'models', 'views',
        'tests', 'test', 'spec', 'specs', 'unit', 'integration',
        'build', 'dist', 'target', 'out', 'output', 'release',
        'config', 'conf', 'settings', 'env', 'environment'
    },
    'writing': {
        'paper', 'thesis', 'manuscript', 'chapters', 'docs', 'references',
        'documentation', 'doc', 'articles', 'posts', 'content',
        'research', 'notes', 'drafts', 'final', 'submission',
        'bibliography', 'citations', 'sources', 'literature'
    },
    'art': {
        'images', 'figures', 'art', 'assets', 'illustrations', 'sketches',
        'portfolio', 'gallery', 'design', 'graphics', 'visuals',
        'photos', 'pictures', 'media', 'resources', 'textures',
        'icons', 'logos', 'banners', 'thumbnails', 'previews'
    }
}


def is_code_file(filename: str) -> bool:
    """
    Check if a file is a code file based on its extension.
    
    Args:
        filename: Name of the file to check
        
    Returns:
        True if the file is a code file, False otherwise
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext in CODE_EXTS


def is_text_file(filename: str) -> bool:
    """
    Check if a file is a text/document file based on its extension.
    
    Args:
        filename: Name of the file to check
        
    Returns:
        True if the file is a text file, False otherwise
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext in TEXT_EXTS


def is_image_file(filename: str) -> bool:
    """
    Check if a file is an image file based on its extension.
    
    Args:
        filename: Name of the file to check
        
    Returns:
        True if the file is an image file, False otherwise
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext in IMAGE_EXTS


def get_file_category(filename: str) -> str:
    """
    Get the category of a file based on its extension.
    
    Args:
        filename: Name of the file to categorize
        
    Returns:
        Category string: 'code', 'text', 'image', 'binary', or 'unknown'
    """
    ext = os.path.splitext(filename)[1].lower()
    
    if ext in CODE_EXTS:
        return 'code'
    elif ext in TEXT_EXTS:
        return 'text'
    elif ext in IMAGE_EXTS:
        return 'image'
    elif ext in OTHER_BINARY_EXTS:
        return 'binary'
    else:
        return 'unknown'
