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

## Example Response

```json
{
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
        }
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
    }
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

## Example: No Git Projects Detected

When uploading a folder without any `.git` directories:

```json
{
  "source": "zip_file",
  "projects": [],
  "overall": {
    "classification": "coding",
    "confidence": 0.712,
    "totals": {
      "projects": 0,
      "files": 5,
      "code_files": 3,
      "text_files": 1,
      "image_files": 1
    }
  }
}
```

**Note:** When no Git projects are detected:
- The `projects` array is empty
- Files are still analyzed and counted in `overall.totals`
- Individual files are NOT listed (since they don't belong to any project)
- Classification and totals still work normally

## Notes

- Files within `.git` directories are excluded from the output
- Only filenames are shown (not full paths) in the `files` arrays
- Contributors are sorted by commit count (descending)
- Projects are identified by the presence of a `.git` directory
- Files outside of any Git project are still counted in `overall.totals` but not listed under any project

