"""Central place for file extension categories used across the app.

This module defines EXT_IMAGE, EXT_CODE and EXT_CONTENT sets so multiple
modules can import them instead of duplicating the lists.
"""

EXT_IMAGE = {
    '.png', '.jpg', '.jpeg', '.svg', '.psd', '.gif', '.tiff', '.tif',
    '.bmp', '.webp', '.ico', '.raw', '.cr2', '.nef', '.arw',
    '.ai', '.eps', '.sketch', '.fig'
}

EXT_CODE = {
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

EXT_CONTENT = {
    '.txt', '.md', '.doc', '.docx', '.pdf', '.tex', '.bib',
    '.rtf', '.odt', '.pages',
    '.log'
}
