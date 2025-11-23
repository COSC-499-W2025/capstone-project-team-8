# Backend Setup Instructions

## Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose (for MySQL database)

## Quick Start with Docker

From the project root (`capstone-project-team-8/`):

```bash
docker compose up
```

This starts the Django backend with MySQL database.

**What this does:**

- Starts MySQL 8.0 database container
- Runs Django migrations automatically
- Starts Django development server on `http://localhost:8000`
- All services run together (MySQL, backend, frontend)

## Local Development Setup

### 1. Navigate to Backend Directory

```bash
cd src/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment

Copy the example environment file:

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

The default values work with Docker Compose. For custom MySQL setup, edit `.env` with your credentials.

**About python-decouple:** This package manages environment variables securely, keeping secrets out of your code and Git repository.

### 6. Run Migrations

```bash
python manage.py migrate
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Start Development Server

```bash
python manage.py runserver
```

The Django development server will start at `http://127.0.0.1:8000/`

## Database

This project uses **MySQL** as the database. The connection is configured via environment variables in `.env`.

### Docker Setup (Recommended)

MySQL runs in a Docker container. Start it with:

```bash
docker compose up db
```

### Local MySQL

If using a local MySQL installation, update `.env` with your credentials:

```env
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

## Running Tests

```bash
# Run all tests
python manage.py test ../../tests

# Run specific test file
python manage.py test ../../tests.test_models
```

## Working with the Backend

### Creating New Apps

```bash
python manage.py startapp your_app_name
```

### Making Database Changes

1. Make changes to your models in `models.py`
2. Create migrations:

   ```bash
   python manage.py makemigrations
   ```

3. Apply migrations:

   ```bash
   python manage.py migrate
   ```

### Project Structure

```text
backend/
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example           # Environment template
├── Dockerfile             # Docker configuration
├── app/                   # Django app
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── serializers.py     # DRF serializers
│   └── admin.py           # Admin interface
└── src/                   # Project configuration
    ├── settings.py        # Django settings
    ├── urls.py            # URL routing
    └── wsgi.py            # WSGI configuration
```

### API Development

- Use Django REST Framework for API endpoints
- Add new views in your app's `views.py`
- Create serializers in `serializers.py`
- Configure URLs in your app's `urls.py`
- Include app URLs in main `src/urls.py`

### Deactivating Virtual Environment

When done working:

```bash
deactivate
```

# api/folder-uploads/ JSON Output Example

This endpoint returns a structured JSON response with project information, file classifications, and contributor statistics.

**Project Detection:** Identifies project boundaries

Currently: Git repositories via `.git` folders. A repo with `frontend/` and `backend/` = ONE project.
Future: Folder structure analysis.

Files not in any project → special project with `id: 0`, `root: "(non-git-files)"`.

## Example Response

```json
{
  "send_to_llm": true,
  "scan_performed": true,
  "source": "zip_file",
  "projects": [
    {
      "id": 1,
      "root": "my-project",
      "classification": {
        "type": "coding",
        "confidence": 0.652,
        "features": {
          "total_files": 3,
          "code": 1,
          "text": 1,
          "image": 1
        },
        "languages": [
          "Python"
        ],
        "frameworks": [],
        "resume_skills": [
          "Backend Development",
          "Object-Oriented Programming"
        ]
      },
      "files": {
        "code": [
          {
            "path": "main.py",
            "lines": 127
          }
        ],
        "content": [
          {
            "path": "README.md",
            "length": 1543
          }
        ],
        "image": [
          {
            "path": "logo.png",
            "size": 24567
          }
        ],
        "unknown": []
      },
      "contributors": [
        {
          "name": "John Doe",
          "email": "john@example.com",
          "commits": 15,
          "lines_added": 847,
          "lines_deleted": 123,
          "percent_commits": 60
        },
        {
          "name": "Jane Smith",
          "email": "jane@example.com",
          "commits": 10,
          "lines_added": 456,
          "lines_deleted": 89,
          "percent_commits": 40
        }
      ]
    }
  ],
  "overall": {
    "classification": "coding",
    "confidence": 0.652,
    "totals": {
      "projects": 1,
      "files": 3,
      "code_files": 1,
      "text_files": 1,
      "image_files": 1
    },
    "languages": [
      "Python"
    ],
    "frameworks": [],
    "resume_skills": [
      "Backend Development",
      "Object-Oriented Programming"
    ]
  }
}
```

## Response Structure

### Top Level
- **`source`** (string): Source type, currently always `"zip_file"`
- **`projects`** (array): List of discovered Git projects
- **`overall`** (object): Aggregate statistics across all projects

### Project Object
Each project contains:
- **`id`** (integer): Sequential project identifier (1, 2, 3...)
- **`root`** (string): Project root directory path
- **`classification`** (object): Project type classification
  - **`type`**: One of `"coding"`, `"writing"`, `"art"`, `"mixed:type1+type2"`, or `"unknown"`
  - **`confidence`**: Classification confidence score (0.0 to 1.0)
  - **`features`** (optional): File count breakdown
  - **`languages`** (array, coding projects only): Detected programming languages, sorted by prevalence
  - **`frameworks`** (array, coding projects only): Detected frameworks and libraries
  - **`resume_skills`** (array, coding and art projects only): Inferred professional skills and capabilities (e.g., "Backend Development", "RESTful APIs", "Containerization"). These are resume-appropriate skill concepts, NOT framework names.
- **`files`** (object): Files organized by type
  - **`code`**: Array of code files with `path` and `lines`
  - **`content`**: Array of text/document files with `path` and `length` (characters)
  - **`image`**: Array of image files with `path` and `size` (bytes)
  - **`unknown`**: Array of unclassified file paths
- **`contributors`** (array): Git contribution statistics per author

### Overall Object
- **`classification`** (string): Overall project type
- **`confidence`** (number): Overall classification confidence
- **`totals`** (object): Aggregate file counts
  - **`projects`**: Number of Git repositories discovered
  - **`files`**: Total files (excluding `.git` directory contents)
  - **`code_files`**: Total code files
  - **`text_files`**: Total text/document files
  - **`image_files`**: Total image files
- **`languages`** (array, optional): Aggregated programming languages across all projects
- **`frameworks`** (array, optional): Aggregated frameworks across all projects
- **`resume_skills`** (array, optional): Aggregated professional skills across all projects

## Example: No Git Projects Detected

When uploading a folder without any `.git` directories, files are listed under a special project:

```json
{
  "send_to_llm": true,
  "scan_performed": true,
  "source": "zip_file",
  "projects": [
    {
      "id": 0,
      "root": "(non-git-files)",
      "classification": {
        "type": "coding",
        "confidence": 0.712,
        "features": {
          "total_files": 5,
          "code": 3,
          "text": 1,
          "image": 1
        },
        "languages": [
          "Python",
          "JavaScript",
          "HTML"
        ],
        "frameworks": [],
        "resume_skills": [
          "Full-Stack Development",
          "Object-Oriented Programming"
        ]
      },
      "files": {
        "code": [
          {
            "path": "script.py",
            "lines": 45
          },
          {
            "path": "app.js",
            "lines": 123
          },
          {
            "path": "index.html",
            "lines": 87
          }
        ],
        "content": [
          {
            "path": "notes.txt",
            "length": 234
          }
        ],
        "image": [
          {
            "path": "diagram.png",
            "size": 15678
          }
        ],
        "unknown": []
      },
      "contributors": []
    }
  ],
  "overall": {
    "classification": "coding",
    "confidence": 0.712,
    "totals": {
      "projects": 0,
      "files": 5,
      "code_files": 3,
      "text_files": 1,
      "image_files": 1
    },
    "languages": [
      "Python",
      "JavaScript",
      "HTML"
    ],
    "frameworks": [],
    "resume_skills": [
      "Full-Stack Development",
      "Object-Oriented Programming"
    ]
  }
}
```

**Note:** When no Git projects are detected:
- A special project with `id: 0` and `root: "(non-git-files)"` is created
- All files are listed under this project
- The project uses the overall classification
- `overall.totals.projects` remains `0` (since this isn't a real Git repository)
- No contributors are listed (since there's no Git history)

## Notes

- Files within `.git` directories are excluded from the output
- Only filenames are shown (not full paths) in the `files` arrays
- Contributors are sorted by commit count (descending)
- **Project Detection:** Currently only Git repositories (via `.git` folders) are detected. Future versions will support detection of other project types
- Files not belonging to any detected project are grouped under `id: 0` with `root: "(non-git-files)"`
- The `overall.totals.projects` count excludes the unorganized files project (id=0)
- **Skills Detection:** Skills are automatically inferred from detected languages, frameworks, and file types. Framework names appear in `frameworks` array, while their associated capabilities appear in `resume_skills`

