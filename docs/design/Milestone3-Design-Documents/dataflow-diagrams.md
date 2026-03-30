# Dataflow & System Architecture Diagrams

--- 

This is the layout for our diagrams

## Level 0 DFD — Context Diagram

The system is treated as a single process. External entities interact with the **PortfolioAI** system.

```mermaid
flowchart TD
    U(["👤 User\n(Browser)"])
    AZ(["☁️ Azure OpenAI\nGPT API"])
    OL(["🤖 Ollama Engine\n(Local LLM)"])
    DB[("🗄️ MySQL\nDatabase")]
    RC(["📄 RenderCV CLI\n(Subprocess)"])

    U -- "ZIP upload, profile data,\nresume edits, portfolio config" --> SYS["PortfolioAI\nSystem"]
    SYS -- "Projects, portfolio,\nresume, skills, scores" --> U

    SYS -- "Project data, prompt templates\n(if LLM consent given)" --> AZ
    AZ -- "AI-generated summary,\ncode analysis" --> SYS

    SYS -- "File content + query\n(via LLM microservice)" --> OL
    OL -- "Generated text response" --> SYS

    SYS -- "Read/write users, projects,\nportfolios, resumes" --> DB
    DB -- "Stored records" --> SYS

    SYS -- "Resume YAML" --> RC
    RC -- "PDF binary" --> SYS
```

---

## Level 1 DFD

The system is decomposed into its major processes and the data stores they interact with.

```mermaid
flowchart TD
    U(["👤 User"])
    AZ(["☁️ Azure OpenAI"])
    OL(["🤖 Ollama\n(LLM Microservice)"])
    RC(["📄 RenderCV CLI"])

    DS_USERS[("D1: users")]
    DS_PROJECTS[("D2: projects /\nproject_files /\nproject_languages /\nproject_frameworks")]
    DS_CONTRIB[("D3: contributors /\nproject_contributions")]
    DS_EVAL[("D4: project_evaluations")]
    DS_PORTFOLIO[("D5: portfolios /\nportfolio_projects")]
    DS_RESUME[("D6: resumes")]

    P1["1. User\nAuthentication"]
    P2["2. ZIP Upload\n& Extraction"]
    P3["3. Project Discovery\n& File Classification"]
    P4["4. Code & Content\nAnalysis"]
    P5["5. Project Evaluation\n(Rubric Scoring)"]
    P6["6. AI Summarization"]
    P7["7. Portfolio\nManagement"]
    P8["8. Resume\nGeneration"]
    P9["9. Profile\nManagement"]

    %% Auth flow
    U -- "username + password" --> P1
    P1 -- "JWT access + refresh tokens" --> U
    P1 -- "read/write user record" --> DS_USERS

    %% Upload flow
    U -- "ZIP file + consents" --> P2
    P2 -- "extracted temp files" --> P3

    %% Classification flow
    P3 -- "project metadata,\nfile records" --> DS_PROJECTS
    P3 -- "classified files" --> P4

    %% Analysis flow
    P4 -- "languages, frameworks,\ngit commits, skills" --> DS_PROJECTS
    P4 -- "contributor stats" --> DS_CONTRIB
    P4 -- "analysis results (if consent)" --> P6

    %% Evaluation flow
    P4 -- "project + language info" --> P5
    P5 -- "rubric scores\n(quality/docs/structure/testing)" --> DS_EVAL

    %% AI summarization
    P6 -- "prompt + project data" --> AZ
    AZ -- "AI summary text" --> P6
    P6 -- "LLM file query" --> OL
    OL -- "generated response" --> P6
    P6 -- "summary stored in project" --> DS_PROJECTS

    %% Portfolio management
    U -- "portfolio config,\nproject selections" --> P7
    P7 -- "read projects" --> DS_PROJECTS
    P7 -- "portfolio + project\nmembership records" --> DS_PORTFOLIO
    P7 -- "AI summary request" --> P6
    P7 -- "portfolio data" --> U

    %% Resume generation
    U -- "resume JSON edits,\ntheme selection" --> P8
    P8 -- "read projects/skills" --> DS_PROJECTS
    P8 -- "YAML content" --> RC
    RC -- "PDF binary" --> P8
    P8 -- "resume record" --> DS_RESUME
    P8 -- "PDF / LaTeX" --> U

    %% Profile management
    U -- "bio, photo, social links,\neducation info" --> P9
    P9 -- "update user record" --> DS_USERS
    P9 -- "updated profile" --> U
```

---

## System Architecture Diagram

Shows the deployment layers, containers, and inter-service communication.

```mermaid
flowchart TB
    subgraph CLIENT["Client Tier (Browser)"]
        direction LR
        NEXT["Next.js 15 SPA\n(React 19, Tailwind CSS v4)\nlocalhost:3000"]
    end

    subgraph DOCKER["Docker Compose Network"]
        direction TB

        subgraph API["API Tier"]
            DJANGO["Django 5 + DRF\nJWT Auth · REST API\nSwagger /api/schema/\nport 8000"]
        end

        subgraph DATA["Data Tier"]
            MYSQL[("MySQL 8.0\ncapstone_db\nport 3306")]
        end

        API -- "Django ORM\n(read/write)" --> DATA
    end

    subgraph LLM_SVC["LLM Microservice (Separate Compose)"]
        direction LR
        EXPRESS["Express.js 5\nAPI key auth\nRate limiter (20 req/min)\nport 3001"]
        OLLAMA["Ollama Runner\nmistral:latest\nport 11434"]
        EXPRESS -- "POST /api/generate" --> OLLAMA
    end

    subgraph EXTERNAL["External Services"]
        direction LR
        AZURE["Azure OpenAI\nGPT model\n(portfolio/project summaries)"]
        RENDERCV["RenderCV CLI\n(subprocess)\nYAML → LaTeX → PDF"]
    end

    CLIENT -- "HTTP/REST\nBearer JWT\nport 8000" --> API
    API -- "POST /api/query\nx-api-key header\nport 3001" --> EXPRESS
    API -- "HTTPS\nAzure OpenAI SDK" --> AZURE
    API -- "subprocess call\n(rendercv render)" --> RENDERCV

    subgraph STORAGE["File Storage (Container Filesystem)"]
        TEMP["Temp ZIP extraction\n/tmp/"]
        MEDIA["Media uploads\n/media/ (profile images,\ngenerated PDFs)"]
    end

    API -- "write/clean temp files" --> TEMP
    API -- "serve/store media" --> MEDIA
```

---

### Key Data Stores Summary

| Store | Contents |
|---|---|
| `users` | Credentials, profile, education, social links |
| `projects` | Type, stats, AI summary, LLM consent flag, git metadata |
| `project_files` | Individual file records: type, hash, language, line count |
| `project_languages` | M2M: project ↔ language with file count, primary flag |
| `project_frameworks` | M2M: project ↔ framework with detection method |
| `contributors` / `project_contributions` | Git authors, commit counts, lines added/deleted, % ownership |
| `project_evaluations` | Rubric scores per language: quality, docs, structure, testing (0–100) |
| `portfolios` / `portfolio_projects` | Named collections, ordering, featured flags, cached stats, public slug |
| `resumes` | JSON resume content, RenderCV YAML, theme selection |
