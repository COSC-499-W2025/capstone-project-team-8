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

## Diagrams & Work Breakdown Structure

### Data Flow Diagram (DFD) 📄 [View DFD](./docs/design/DFD.md)
A high-level view of how data moves through the system.

### System Architecture Diagram (SAD) 📄 [View SAD](./docs/design/SAD.md)
Overview of components, services, and infrastructure for the application. This diagram focused mostly on the backend logic since we will spend the majority of the semester building the backend first.

### Work Breakdown Structure (WBS) 📄 [View WBS](./docs/plan/WBS.md)
A brief overview of the work breakdown structure plan.
