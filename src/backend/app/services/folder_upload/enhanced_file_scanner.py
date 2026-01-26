"""
Enhanced File Scanner with Hash Computation

Example implementation showing how to integrate file hashing
during the upload scanning process for deduplication.
"""

import os
from pathlib import Path
from typing import Dict, List, Any
import zipfile

from app.utils.file_hash import compute_file_hash, compute_hash_from_zipfile


class EnhancedFileScannerService:
    """
    Enhanced file scanner that computes content hashes during scan.
    
    This version adds hash computation to enable deduplication
    while maintaining backward compatibility with existing code.
    """
    
    EXCLUDED_DIRS = {
        'node_modules', '__pycache__', 'venv', 'env',
        'dist', 'build', '.next', '.nuxt', 'vendor', 'target',
        'coverage', '.pytest_cache', '.mypy_cache', '.venv',
        '.tox', '.eggs', '*.egg-info', '.gradle', 'out',
        'bin', 'obj', '.vs', '.idea', '.vscode',
    }
    
    def scan_with_hashing(
        self,
        tmpdir_path: Path,
        zip_path: Path,
        projects: Dict[Path, int],
        projects_rel: Dict[int, str]
    ) -> List[Dict[str, Any]]:
        """
        Scan files and compute content hashes from original ZIP.
        
        This method enhances the standard scan by:
        1. Computing SHA256 hash for each file directly from ZIP
        2. Including hash in result dictionary
        3. Enabling downstream deduplication
        
        Args:
            tmpdir_path: Path to extracted directory
            zip_path: Path to original ZIP file
            projects: Mapping of project root paths to numeric tags
            projects_rel: Mapping of numeric tags to relative root paths
            
        Returns:
            List of file analysis results with content_hash field
        """
        results = []
        
        # Open ZIP for hash computation
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for root, dirs, files in os.walk(tmpdir_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS]
                
                for fname in files:
                    fpath = Path(root) / fname
                    
                    # Get relative path for ZIP lookup
                    try:
                        rel_path = fpath.relative_to(tmpdir_path)
                        rel_path_str = rel_path.as_posix()
                    except ValueError:
                        rel_path_str = fname
                    
                    # Basic file analysis (simplified)
                    result = self._analyze_file(fpath)
                    result['path'] = rel_path_str
                    
                    # Compute hash from ZIP (avoids extraction corruption)
                    content_hash = compute_hash_from_zipfile(zf, rel_path_str)
                    if content_hash:
                        result['content_hash'] = content_hash
                    
                    # Assign project tag
                    self._assign_project_tag(result, projects_rel)
                    
                    results.append(result)
        
        return results
    
    def _analyze_file(self, fpath: Path) -> Dict[str, Any]:
        """
        Analyze a single file using the proper analyzer functions.
        
        Uses analyze_image, analyze_code, analyze_content from file_analyzers
        to ensure all metrics (bytes, chars, lines) are populated correctly.
        """
        from app.services.classifiers import classify_file
        from app.services.analysis.analyzers.file_analyzers import analyze_code, analyze_content, analyze_image
        
        kind = classify_file(fpath)
        
        if kind == 'code':
            # Use the proper code analyzer to get lines, chars, and bytes
            result = analyze_code(fpath)
        
        elif kind == 'content':
            # Use the proper content analyzer to get all metrics
            result = analyze_content(fpath)
            
            # For content files, we need to include the actual text for LLM and hash computation
            # Always add text field even if file is skipped (tests and LLM may need it)
            try:
                if fpath.suffix.lower() == '.pdf':
                    from app.services.utils.pdfReader import read_pdf
                    text = read_pdf(str(fpath))
                    if text is None:
                        text = ""  # fallback for failed PDF reads
                else:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                
                # Add text to result (always include it for content files)
                result['text'] = text[:20000]  # Cap at 20KB
                result['truncated'] = len(text) > 20000
            except Exception:
                pass
        
        elif kind == 'image':
            # Use the proper image analyzer to get size and bytes
            result = analyze_image(fpath)
        
        else:
            # Unknown file type
            result = {'type': 'unknown'}
        
        return result
    
    def _assign_project_tag(
        self,
        result: Dict[str, Any],
        projects_rel: Dict[int, str]
    ) -> None:
        """Assign project tag based on file path."""
        p = result.get('path', '')
        for tag, root_str in projects_rel.items():
            if p == root_str or p.startswith(root_str + '/'):
                result['project_tag'] = tag
                result['project_root'] = root_str
                break


# Integration example for UploadFolderView
def example_integration_in_upload_view():
    """
    Example showing how to integrate enhanced scanner in upload view.
    
    Add this to your UploadFolderView.post() method:
    """
    code_example = '''
    # In uploadFolderView.py, replace the existing scan call:
    
    # OLD:
    # results = self.file_scanner.scan(tmpdir_path, projects, projects_rel)
    
    # NEW (with hashing):
    from app.services.folder_upload.enhanced_file_scanner import EnhancedFileScannerService
    
    enhanced_scanner = EnhancedFileScannerService()
    results = enhanced_scanner.scan_with_hashing(
        tmpdir_path=extract_dir,
        zip_path=tmp_zip_path,  # Path to saved ZIP file
        projects=projects,
        projects_rel=projects_rel
    )
    
    # The results will now include 'content_hash' field
    # which database_service.py will use for deduplication
    '''
    return code_example


# Example: Direct usage
def example_usage():
    """
    Complete example of using the enhanced scanner.
    """
    example = '''
    import tempfile
    import zipfile
    from pathlib import Path
    
    # Extract ZIP
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_zip_path = Path(tmpdir) / "upload.zip"
        extract_dir = Path(tmpdir) / "extracted"
        
        # Save uploaded file
        with open(tmp_zip_path, 'wb') as f:
            for chunk in upload.chunks():
                f.write(chunk)
        
        # Extract
        with zipfile.ZipFile(tmp_zip_path, 'r') as zf:
            zf.extractall(extract_dir)
        
        # Discover projects (existing code)
        projects = discover_projects(extract_dir)
        projects_rel = build_projects_rel(projects, extract_dir)
        
        # Scan with hashing (NEW)
        scanner = EnhancedFileScannerService()
        results = scanner.scan_with_hashing(
            tmpdir_path=extract_dir,
            zip_path=tmp_zip_path,
            projects=projects,
            projects_rel=projects_rel
        )
        
        # Results now include content_hash for deduplication
        for result in results[:3]:
            print(f"File: {result['path']}")
            print(f"Hash: {result.get('content_hash', 'N/A')}")
            print(f"Type: {result['type']}")
            print()
    '''
    return example
