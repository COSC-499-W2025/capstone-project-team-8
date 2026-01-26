"""
File Hashing Utilities for Deduplication

Provides functions to compute content hashes for uploaded files
to enable duplicate detection across uploads.
"""

import hashlib
from typing import BinaryIO, Optional


def compute_file_hash(file_content: bytes) -> str:
    """
    Compute SHA256 hash of file content.
    
    Args:
        file_content: Raw bytes of the file
        
    Returns:
        SHA256 hash as hexadecimal string
        
    Example:
        >>> content = b"Hello, World!"
        >>> hash_value = compute_file_hash(content)
        >>> print(hash_value)
        'dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f'
    """
    return hashlib.sha256(file_content).hexdigest()


def compute_file_hash_from_stream(file_stream: BinaryIO, chunk_size: int = 8192) -> str:
    """
    Compute SHA256 hash of file content from a stream.
    Useful for large files to avoid loading entire content into memory.
    
    Args:
        file_stream: File-like object opened in binary mode
        chunk_size: Number of bytes to read per iteration
        
    Returns:
        SHA256 hash as hexadecimal string
        
    Example:
        >>> with open('myfile.txt', 'rb') as f:
        ...     hash_value = compute_file_hash_from_stream(f)
    """
    sha256_hash = hashlib.sha256()
    
    # Read file in chunks to handle large files efficiently
    for chunk in iter(lambda: file_stream.read(chunk_size), b''):
        sha256_hash.update(chunk)
    
    return sha256_hash.hexdigest()


def compute_text_hash(text: str) -> str:
    """
    Compute SHA256 hash of text content.
    
    Args:
        text: String content to hash
        
    Returns:
        SHA256 hash as hexadecimal string
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def compute_hash_from_zipfile(zip_file, file_path: str) -> Optional[str]:
    """
    Compute hash of a file inside a ZIP archive.
    
    Args:
        zip_file: zipfile.ZipFile object
        file_path: Path of file within the ZIP
        
    Returns:
        SHA256 hash as hexadecimal string, or None if file not found
        
    Example:
        >>> import zipfile
        >>> with zipfile.ZipFile('upload.zip', 'r') as zf:
        ...     hash_value = compute_hash_from_zipfile(zf, 'project/main.py')
    """
    try:
        with zip_file.open(file_path) as f:
            content = f.read()
            return compute_file_hash(content)
    except KeyError:
        # File not found in ZIP
        return None
    except Exception:
        # Handle other errors (permission, corruption, etc.)
        return None
