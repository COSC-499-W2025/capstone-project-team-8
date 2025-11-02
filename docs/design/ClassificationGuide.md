# Project Classification Guide

## Overview

The project classifier is a heuristic-based system that analyzes uploaded zip files and classifies them into different project types based on file extensions, folder structure, and content patterns. It supports three main categories: **coding**, **writing**, and **art**, with the ability to detect **mixed** projects that exhibit characteristics of multiple categories.

## Classification Categories

### 1. Coding Projects
Projects primarily focused on software development, programming, and technical implementation.

**Examples:**
- Web applications (HTML, CSS, JavaScript)
- Python scripts and applications
- Mobile app development
- Data science projects
- System administration scripts

### 2. Writing Projects
Projects focused on content creation, documentation, research, and written materials.

**Examples:**
- Academic papers and theses
- Technical documentation
- Blog posts and articles
- Research manuscripts
- User guides and manuals

### 3. Art Projects
Projects focused on visual content, design, and creative assets.

**Examples:**
- Digital art portfolios
- Graphic design projects
- Photography collections
- UI/UX design files
- Illustration projects

### 4. Mixed Projects
Projects that exhibit characteristics of multiple categories, indicating diverse content types.

**Examples:**
- Research projects with code and documentation
- Web development with design assets
- Data science with visualizations and reports

## File Type Classification

### Code Files
The classifier recognizes the following file extensions as code:

**Programming Languages:**
- `.py`, `.pyw`, `.pyi` - Python
- `.js`, `.jsx`, `.mjs`, `.cjs` - JavaScript
- `.ts`, `.tsx` - TypeScript
- `.java`, `.jsp` - Java
- `.c`, `.h`, `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hh` - C/C++
- `.cs` - C#
- `.go` - Go
- `.rs` - Rust
- `.php`, `.php3`, `.php4`, `.php5`, `.phtml` - PHP
- `.rb` - Ruby
- `.swift` - Swift
- `.kt`, `.kts` - Kotlin
- `.scala`, `.sc` - Scala
- `.hs`, `.lhs` - Haskell
- `.erl`, `.ex`, `.exs` - Erlang/Elixir
- `.fs`, `.fsi` - F#
- `.vb` - Visual Basic
- `.r` - R
- `.jl` - Julia
- `.dart` - Dart
- `.lua` - Lua
- `.pl`, `.pm` - Perl
- `.groovy` - Groovy

**Web Technologies:**
- `.html`, `.htm` - HTML
- `.css` - CSS

**Configuration & Data:**
- `.json` - JSON
- `.xml` - XML
- `.yaml`, `.yml` - YAML
- `.toml` - TOML
- `.ini`, `.cfg`, `.conf` - Configuration files

**Scripts & Automation:**
- `.sh`, `.bash`, `.zsh` - Shell scripts
- `.ps1`, `.psm1` - PowerShell
- `.bat`, `.cmd` - Windows batch files

**Other:**
- `.sql` - SQL
- `.asm`, `.s` - Assembly
- `.ipynb` - Jupyter notebooks

### Text Files
The classifier recognizes the following file extensions as text content:

**Documents:**
- `.txt` - Plain text
- `.md` - Markdown
- `.doc`, `.docx` - Microsoft Word
- `.pdf` - PDF documents
- `.tex` - LaTeX
- `.bib` - BibTeX
- `.rtf` - Rich Text Format
- `.odt` - OpenDocument Text
- `.pages` - Apple Pages

**Logs:**
- `.log` - Log files

### Image Files
The classifier recognizes the following file extensions as images:

**Raster Images:**
- `.png` - PNG
- `.jpg`, `.jpeg` - JPEG
- `.gif` - GIF
- `.tiff`, `.tif` - TIFF
- `.bmp` - Bitmap
- `.webp` - WebP
- `.ico` - Icon
- `.raw`, `.cr2`, `.nef`, `.arw` - Raw camera formats

**Vector Images:**
- `.svg` - Scalable Vector Graphics
- `.psd` - Photoshop
- `.ai` - Adobe Illustrator
- `.eps` - Encapsulated PostScript
- `.sketch` - Sketch
- `.fig` - Figma

## Scoring System

### Base Scoring
The classifier uses a weighted scoring system based on file type ratios:

```python
# Default weights
code_weight = 3.0
text_weight = 2.0
image_weight = 2.5

# Calculate base scores
score_code = (code_files / total_files) * code_weight
score_text = (text_files / total_files) * text_weight
score_image = (image_files / total_files) * image_weight
```

### Folder Structure Bonuses
The classifier analyzes folder names to provide additional scoring hints:

**Code Project Hints:**
- `src`, `lib`, `bin`, `app`, `srcs`, `source`, `sources`
- `code`, `scripts`, `utils`, `helpers`, `core`, `modules`
- `components`, `services`, `controllers`, `models`, `views`
- `tests`, `test`, `spec`, `specs`, `unit`, `integration`
- `build`, `dist`, `target`, `out`, `output`, `release`
- `config`, `conf`, `settings`, `env`, `environment`

**Writing Project Hints:**
- `paper`, `thesis`, `manuscript`, `chapters`, `docs`, `references`
- `documentation`, `doc`, `articles`, `posts`, `content`
- `research`, `notes`, `drafts`, `final`, `submission`
- `bibliography`, `citations`, `sources`, `literature`

**Art Project Hints:**
- `images`, `figures`, `art`, `assets`, `illustrations`, `sketches`
- `portfolio`, `gallery`, `design`, `graphics`, `visuals`
- `photos`, `pictures`, `media`, `resources`, `textures`
- `icons`, `logos`, `banners`, `thumbnails`, `previews`

**Folder Bonus:** +1.5 points for matching folder hints

### Additional Scoring Bonuses

**README Files:** +0.5 points for coding, +0.1 points for writing
- Detected by: files containing "readme" in name or `.md`/`.txt` extensions

**Requirements Files:** +0.5 points for coding
- Detected by: files containing "requirements" in name or `.txt` extensions

**License Files:** +0.5 points for coding
- Detected by: files containing "license" in name or `.txt`/`.md` extensions

**Package Files:** +0.3 points for coding
- Detected by: `.json`, `.toml`, `.yaml`, `.yml`, `.ini`, `.cfg` extensions

## Classification Logic

### 1. File Count Validation
- **Minimum files:** 2 files required for confident classification
- **Empty projects:** Return "unknown"
- **Too few files:** Return "unknown"

### 2. Score Calculation
1. Calculate file type ratios
2. Apply base weights (3.0, 2.0, 2.5)
3. Add folder structure bonuses
4. Add additional file bonuses

### 3. Mixed Project Detection
The classifier uses two conditions to detect mixed projects:

**Condition 1:** Close scores with high values
```python
score_difference < margin_threshold and top_score > 1.0 and second_score > 0.8
```

**Condition 2:** Multiple file types with decent scores
```python
has_multiple_types and top_score > 0.8 and second_score > 0.5 and score_difference < 1.0
```

**Mixed Project Format:** `mixed:category1+category2`
- Examples: `mixed:coding+art`, `mixed:writing+coding`

### 4. Final Classification
- **Mixed detected:** Return `mixed:top_category+second_category`
- **Single category:** Return the highest scoring category
- **Tie/Unclear:** Return the highest scoring category

## Configuration Parameters

### Core Parameters
- **`min_files_for_confident`:** Minimum files needed (default: 2)
- **`weights`:** Tuple of (code_weight, text_weight, image_weight) (default: 3.0, 2.0, 2.5)
- **`folder_bonus`:** Bonus for matching folder hints (default: 1.5)
- **`margin_threshold`:** Minimum score difference to avoid mixed classification (default: 0.25)
- **`force_mixed`:** Enable/disable mixed detection (default: True)

### Tuning Guidelines

**For More Sensitive Classification:**
- Decrease `min_files_for_confident` to 1
- Increase `folder_bonus` to 2.0-3.0
- Decrease `margin_threshold` to 0.1-0.2

**For More Conservative Classification:**
- Increase `min_files_for_confident` to 3-5
- Decrease `folder_bonus` to 1.0
- Increase `margin_threshold` to 0.5-1.0

**For Custom Weights:**
- Increase `code_weight` to emphasize code files
- Increase `image_weight` to emphasize visual content
- Increase `text_weight` to emphasize documentation

## Confidence Scoring

The classifier provides confidence scores based on:

**Base Confidence:**
```python
max_ratio = max(code_ratio, text_ratio, image_ratio)
base_confidence = max_ratio * 1.5
```

**File Count Boost:**
```python
file_boost = min(total_files * 0.1, 0.3)
confidence = min(base_confidence + file_boost, 1.0)
```

**Confidence Levels:**
- **High (>0.7):** Clear, dominant file type with many files
- **Medium (0.4-0.7):** Moderate confidence with some ambiguity
- **Low (<0.4):** Unclear patterns or few files

## API Integration

### Upload Folder View
The classifier integrates with the `UploadFolderView` to provide:

**Project Detection:**
- Git repository discovery via .git folders
- Project boundary identification
- Sequential project ID assignment

**Classification:**
- Overall zip file classification
- Individual project classifications
- Mixed project detection
- Confidence scoring

**Response Format:**
```json
{
  "source": "zip_file",
  "projects": [
    {
      "id": 1,
      "root": "project1",
      "classification": {
        "type": "mixed:coding+art",
        "confidence": 0.800,
        "features": {
          "total_files": 3,
          "code": 1,
          "text": 1,
          "image": 1
        }
      },
      "files": {
        "code": [
          {
            "path": "main.py",
            "lines": 45
          }
        ],
        "content": [
          {
            "path": "README.md",
            "length": 1205
          }
        ],
        "image": [
          {
            "path": "logo.png",
            "size": 15234
          }
        ],
        "unknown": []
      },
      "contributors": []
    }
  ],
  "overall": {
    "classification": "mixed:coding+art",
    "confidence": 0.800,
    "totals": {
      "projects": 1,
      "files": 3,
      "code_files": 1,
      "text_files": 1,
      "image_files": 1
    }
  }
}
```

**Response Structure Details:**

**Top Level:**
- `source`: Source type (currently always "zip_file")
- `projects`: Array of discovered projects
- `overall`: Aggregate statistics and classification

**Project Object (`projects` array):**
- `id`: Numeric project identifier (1, 2, 3...)
- `root`: Project root directory path
- `classification`: Project type analysis
  - `type`: Classification ("coding", "writing", "art", "mixed:type1+type2", "unknown")
  - `confidence`: Confidence score (0.0 to 1.0)
  - `features`: File count breakdown
    - `total_files`: Total files in project
    - `code`: Number of code files
    - `text`: Number of text files
    - `image`: Number of image files
- `files`: Files organized by type
  - `code`: Array of `{path, lines}` objects
  - `content`: Array of `{path, length}` objects
  - `image`: Array of `{path, size}` objects
  - `unknown`: Array of file path strings
- `contributors`: Git contributor information (if applicable)

**Overall Object:**
- `classification`: Overall project type across all projects
- `confidence`: Overall confidence score
- `totals`: Aggregate file counts
  - `projects`: Number of Git repositories detected
  - `files`: Total files (excluding .git directory contents)
  - `code_files`: Total code files
  - `text_files`: Total text files
  - `image_files`: Total image files

**File Path Note:** Only filenames are shown in the `files` arrays (not full paths)

## Examples

### Pure Coding Project
```
project/
├── src/
│   ├── main.py
│   ├── utils.py
│   └── config.py
├── tests/
│   └── test_main.py
├── requirements.txt
└── README.md
```
**Result:** `coding` (high confidence)

### Pure Art Project
```
portfolio/
├── images/
│   ├── artwork1.png
│   ├── artwork2.jpg
│   └── design.svg
├── sketches/
│   └── sketch1.psd
└── gallery/
    └── preview.gif
```
**Result:** `art` (high confidence)

### Mixed Project
```
research/
├── analysis.py
├── data_processing.py
├── paper.tex
├── figures/
│   ├── chart1.png
│   └── diagram.svg
└── README.md
```
**Result:** `mixed:coding+writing` (medium confidence)

### Writing Project
```
thesis/
├── chapters/
│   ├── introduction.tex
│   ├── methodology.tex
│   └── conclusion.tex
├── references/
│   └── bibliography.bib
└── figures/
    └── diagram.pdf
```
**Result:** `writing` (high confidence)

## Troubleshooting (For Development)

### Common Issues

**1. Projects Classified as "unknown"**
- Check if project has at least 2 files
- Verify file extensions are recognized
- Consider adding more files or adjusting `min_files_for_confident`

**2. Unexpected Mixed Classifications**
- Review file type distribution
- Check folder structure for hints
- Adjust `margin_threshold` parameter

**3. Low Confidence Scores**
- Add more files of the dominant type
- Improve folder structure with relevant hints
- Consider the project's actual content diversity

### Debugging Tips

1. **Check file counts:** Ensure sufficient files for classification
2. **Review folder names:** Use descriptive folder names that match project type
3. **Examine file extensions:** Ensure files have recognized extensions
4. **Test with different weights:** Adjust parameters for your specific use case
5. **Consider project context:** Some projects may legitimately be mixed

## Future Enhancements

Potential improvements to the classification system:

1. **Machine Learning Integration:** Train models on labeled datasets
2. **More Specific Classification:** Recognize specific frameworks (Python-Django, Node-React, etc.)
3. **Non-Git Project Detection:** Folder structure pattern analysis for projects without .git
4. **Custom Rules:** Allow user-defined classification rules
5. **Confidence Calibration:** Improve confidence score accuracy


---

*This guide covers the current implementation of the project classifier. For technical details, refer to the source code in `src/backend/app/services/project_classifier.py`.*
