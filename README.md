# Capstone Project - Team 8

A web application that enables users to upload, scan, and analyze their work artifacts. The app helps organize and showcase selected files via a dashboard, allowing users to export a portfolio folder for employers to review their skills and growth.

<img width="1891" height="939" alt="image" src="https://github.com/user-attachments/assets/7f354905-3b3d-442f-8a18-6709c0a0a5e0" />

- **Course:** COSC 499 (Winter 2025)  
- **Team:** Team 8
- **Team Members**:
    - Jordan Truong
    - Kyle Porter
    - Charlie Schwebius
    - Harper Kerstens
    - Matin Raoufi
    - Kyle McLeod




## Quick Start with Docker

### Prerequisites
- Docker Desktop installed and running
- Git installed

### Running the Project

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd capstone-project-team-8
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Run database migrations**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Django Admin: http://localhost:8000/admin
   - **API Documentation:**
     - Swagger UI: http://localhost:8000/api/schema/swagger-ui/
     - ReDoc: http://localhost:8000/api/schema/redoc/
     - OpenAPI Schema: http://localhost:8000/api/schema/

### Testing files
We have included three sample ZIP files:
These Two files reflect the same project, one at an early stage and the same project at a later stage.
[Original](testfolders/testfolder-33-Original.zip)
[Updated](testfolders/testfolder-33-Updated.zip)
This folder has a variety of projects including both a individual and collaborative coding project
[Collaborative Project](testfolders/testfolder-34.zip)

### Stopping the Project
```bash
docker-compose down
```

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuilding After Changes
```bash
docker-compose up -d --build
```




## Technology Stack

### Frontend 📄 [Frontend Documentation](./src/frontend/README.md)

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 13+ | React framework with SSR |
| React | 18+ | Reusable components & Next.js built on React|
| Tailwind CSS | Latest | Utility-first CSS styling |
| JavaScript | ES6+ | Primary frontend language |

### Backend 📄 [Backend Documentation](./src/backend/README.md)

| Technology | Version | Purpose |
|------------|---------|---------|
| Django | 4.2+ | Python web framework |
| Django REST Framework | Latest | API development |
| Python | 3.8+ | Backend programming language |
| MySQL | 8.0+ | Primary data storage |
| MySQL | Latest | Development database |
| Docker | Latest | Containerization |

### LLM Microservice 📄 [LLM Documentation](./src/llm-service/README.md)

| Technology | Version | Purpose |
|------------|---------|---------|
| Express.js | 5.1.0+ | Open up API route |
| Ollama | Latest | Run AI model |
| llama3.1:8b | Latest |AI model |
| gemini-2.5-flash | 2.5-flash |AI model |

## Diagrams & Work Breakdown Structure

### Level 0 Context Diagram 📄 [View Context Diagram](./docs/design/Milestone3-Design-Documents/FinalFlowChart.png)
A low-level view of the system's main components and how they interact with each other and external entities.

### Level 1 Data Flow Diagram (DFD) 📄 [View DFD](./docs/design/Milestone3-Design-Documents/DFD1Final.png)
A high-level view of how data moves through the system.

### System Architecture Diagram (SAD) 📄 [View SAD](./docs/design/Milestone3-Design-Documents/SystemArchitechtureFinal.png)
Overview of components, services, and infrastructure for the application. This diagram focused mostly on the backend logic since we will spend the majority of the semester building the backend first.

### Work Breakdown Structure (WBS) 📄 [View WBS](./docs/plan/WBS.md)
A brief overview of the work breakdown structure plan.

### List of known bugs
[docs/BugList.docx](./docs/BugList.docx)

## Test report

This report documents which automated tests are expected to run successfully on the current codebase, and the strategy used to keep the system stable.

### How to run

1. **Frontend tests (Jest)**: run from `src/frontend`
   - `cd src/frontend`
   - `npm test`

2. **Backend tests (Django unittest)**: run from the repo root with Docker Compose
   - `docker compose build backend`
   - `docker compose up -d db`
   - `docker compose run --rm backend python manage.py test --exclude-tag=llm`

### What the tests cover

- **Frontend:** Jest tests under `src/frontend/src/__tests__/` cover key user flows and UI/business logic behavior. They typically use mocked network/API boundaries so failures are deterministic and regressions are caught early.
- **Backend:** Django tests under the top-level `tests/` folder validate the core parsing/classification pipeline and API endpoint behavior. CI runs with `--exclude-tag=llm` to avoid nondeterminism when LLM services are not available.

### GitHub Actions (auto tests)

- **`frontend_tests.yml`** runs frontend Jest tests on `push` to `main` and on `pull_request`.
- **`backend_tests.yml`** builds/runs the backend container, starts the database, and runs Django tests with LLM-tag exclusion on `push` to `main` and on `pull_request`.
