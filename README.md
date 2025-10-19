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

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Node.js 18+

### Development Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd capstone-project-team-8
   ```

2. **Start all services with Docker**

   ```bash
   docker compose up
   ```

   This starts:
   - MySQL database on `localhost:3306`
   - Django backend on `localhost:8000`
   - Next.js frontend on `localhost:3000`

3. **Backend setup (local development)**

   ```bash
   cd src/backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Copy environment template
   cp .env.example .env
   
   # Run migrations
   python manage.py migrate
   
   # Run tests
   python manage.py test ../../tests
   ```

### Environment Variables

The backend requires a `.env` file. Copy `.env.example` and update values:

```bash
cd src/backend
cp .env.example .env
```

Default values work with Docker Compose setup.

### Running Tests

```bash
cd src/backend
python manage.py test ../../tests
```

## 📚 Documentation Links

# [Data Flow Diagram](./docs/design/DFD.md)

# [System Architecture Diagram](./docs/design/SAD.md)

# [Work Breakdown Structure](./docs/plan/WBS.md)
