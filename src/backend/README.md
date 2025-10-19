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
