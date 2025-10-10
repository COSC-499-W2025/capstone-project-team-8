[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=20510450&assignment_repo_type=AssignmentRepo)
# Project-Starter
Please use the provided folder structure for your project. You are free to organize any additional internal folder structure as required by the project. 

```
.
├── docs                    # Documentation files
│   ├── contract            # Team contract
│   ├── proposal            # Project proposal 
│   ├── design              # UI mocks
│   ├── minutes             # Minutes from team meetings
│   ├── logs                # Team and individual Logs
│   └── ...          
├── src                     # Source files (alternatively `app`)
├── backend                 # Django backend
│   ├── src                 # Django project files
│   └── requirements.txt    # Python dependencies
├── tests                   # Automated tests 
├── utils                   # Utility files
└── README.md
```

Please use a branching workflow, and once an item is ready, do remember to issue a PR, review, and merge it into the master branch.
Be sure to keep your docs and README.md up-to-date.

# Backend Setup Instructions

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

## Setup Steps

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment (Recommended)
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
pip install django djangorestframework
```

Or if you have a requirements.txt file:
```bash
pip install -r requirements.txt
```

### 5. Navigate to Django Project
```bash
cd src
```

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

## Working with the Backend

### Creating New Apps
```bash
cd backend/src
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

### Running Tests
```bash
python manage.py test
```

### Project Structure
```
backend/
├── src/                    # Main Django project
│   ├── manage.py          # Django management script
│   ├── src/               # Project configuration
│   │   ├── settings.py    # Django settings
│   │   ├── urls.py        # URL routing
│   │   └── wsgi.py        # WSGI configuration
│   ├── app/               # Example Django app
│   └── db.sqlite3         # SQLite database (generated)
└── requirements.txt       # Python dependencies
```

### API Development
- Use Django REST Framework for API endpoints
- Add new views in your app's `views.py`
- Configure URLs in your app's `urls.py`
- Include app URLs in main `src/urls.py`

### Deactivating Virtual Environment
When done working:
```bash
deactivate
```