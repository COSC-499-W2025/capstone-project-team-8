# Milestone 1 Status Report

**Date:** October 30, 2025  
**Team:** Team 8  
**Project:** Portfolio Analysis & Organization Platform

---

## 📊 Overall Progress

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Complete | 6 | 30% |
| 🚧 Partial/In Progress | 6 | 30% |
| ❌ Not Started | 8 | 40% |

---

## ✅ Completed Requirements (6/20)

### 1. ✅ Parse a specified zipped folder containing nested folders and files

**Status:** Complete  
**Implementation:**

- `uploadFolderView.py` handles ZIP file uploads via `/api/upload-folder/` endpoint
- Extracts and walks through nested directory structures
- Supports POST with multipart form data
- Tests: `test_upload_folder.py` (test_post_zip, test_nested_folders)

### 2. ✅ Return an error if the specified file is in the wrong format

**Status:** Complete  
**Implementation:**

- Validates file is a ZIP archive using `zipfile.is_zipfile()`
- Returns 400 error with message "Uploaded file is not a zip archive"
- Tests: `test_upload_folder.py` (test_non_zip_upload, test_missing_file)

### 3. ✅ Distinguish individual projects from collaborative projects

**Status:** Complete  
**Implementation:**

- `analyzers.py::discover_git_projects()` scans for `.git` directories
- Assigns unique `project_tag` and `project_root` to discovered repositories
- Supports multiple Git projects within a single ZIP
- Tests: `test_upload_folder.py` (test_project_tag_single_repo, test_project_tag_multiple_repos)

### 4. ✅ For a coding project, identify the programming language and framework used

**Status:** Complete  
**Implementation:**

- `project_classifier.py` identifies 100+ file extensions for various programming languages
- Classifies projects as: coding, writing, art, or mixed
- Detects frameworks through folder structure analysis (src/, lib/, tests/, etc.)
- Returns classification with confidence scores
- Tests: `test_project_classifier.py`, `test_upload_folder_with_classifier.py`

### 5. ✅ Extrapolate individual contributions for a given collaboration project

**Status:** Complete  
**Implementation:**

- `analyzers.py::analyze_git_repository()` extracts contributor statistics
- Provides per-author metrics: commit counts, lines added/deleted, files changed
- `analyzers.py::analyze_file_blame()` shows line-by-line contributions
- Git integration using subprocess calls to git CLI
- Tests: Validated through upload folder tests with Git repositories

### 6. ✅ Output all the key information for a project

**Status:** Complete  
**Implementation:**

- `/api/upload-folder/` returns comprehensive JSON response:
  - File-level analysis (type, path, metrics)
  - Project tags and roots
  - Git analysis (contributors, commits, line changes)
  - Project classifications (type, confidence, features)
- Structured output for all discovered projects

---

## 🚧 Partial/In Progress Requirements (6/20)

### 6. 🚧 Extract key contribution metrics in a project, displaying information about the duration of the project and activity type contribution frequency (e.g., code vs test vs design vs document), and other important information

**Status:** Partial (85%)  
**Current Implementation:**

- Displays commit counts per contributor
- Tracks lines added/deleted per author
- Counts files changed per contributor
- Identifies total contributor count
- Returns structured JSON with all metrics
- File types classified: code (with line counts), images (with sizes), content (with character counts)

**Missing:**

- Project duration/timeline extraction from Git history
- First commit to last commit date range
- Activity type contribution frequency breakdown (code vs test vs design vs document)

### 7. 🚧 Store project information into a database

**Status:** Partial (30%)  
**Current Implementation:**

- MySQL database configured in `settings.py` (capstone_db)
- User model created with authentication support (`models.py`)
- Database migrations created (`0001_initial.py`)
- Docker Compose setup for MySQL 8.0
- Tests: `test_models.py`, `test_user_model.py` verify user database operations

**Missing:**

- Project model to store project data
- File/artifact model to store analyzed files
- Portfolio model to store portfolio configurations
- Database endpoints to save/retrieve project information
- No project data persistence (only returns JSON, doesn't save)

**Missing:**

- Project/File/Portfolio models
- Database persistence for analyzed projects

### 9. 🚧 Require the user to give consent for data access before proceeding

**Status:** Not Started (0%)  
**Current Implementation:**

- User authentication system in place (login/register endpoints)

**Missing:**

- Consent flow in frontend
- Terms of service acceptance
- Data access consent tracking
- Cookie/tracking consent

### 10. 🚧 Request user permission before using external services (e.g., LLM) and provide implications on data privacy about the user's data

**Status:** Not Started (0%)  
**Note:** LLM service infrastructure exists on `LLM-security` branch but not merged to main yet.

**Missing:**

- Frontend UI for consent prompts
- User preference storage for LLM usage
- Privacy implications disclosure
- Privacy policy documentation
- User-facing privacy notices
- Data retention policies
- GDPR/privacy compliance checks
- LLM service integration in main branch

### 11. 🚧 Have alternative analyses in place if sending data to an external service is not permitted

**Status:** In Progress (60%)  
**Current Implementation:**

- Local analysis already works: file classification, Git analysis, project classification
- Can function without LLM service

**Missing:**

- Fallback logic when LLM is disabled
- Alternative skill extraction methods
- Non-LLM summarization

### 12. 🚧 Store user configurations for future use

**Status:** In Progress (40%)  
**Current Implementation:**

- User model stores basic user data
- Database infrastructure ready

**Missing:**

- Configuration model for user preferences
- API endpoints to save/retrieve configs
- Frontend settings interface

---

## ❌ Not Started Requirements (7/20)

### 14. ❌ Extract key skills from a given project
**Status:** Not Started  
**Planned Approach:**
- Use LLM to analyze code and extract skills
- Parse README files for technology mentions
- Analyze package.json, requirements.txt, etc. for dependencies
- Map file extensions to technology skills

### 15. ❌ Retrieve previously generated portfolio information
**Status:** Not Started  
**Requirements:**
- Portfolio model in database
- API endpoint: GET `/api/portfolio/{id}`
- Store portfolio configurations per user

### 16. ❌ Retrieve previously generated résumé item
**Status:** Not Started  
**Requirements:**
- Resume/CV model in database
- API endpoint: GET `/api/resume/{id}`
- Store resume items linked to projects

### 17. ❌ Rank importance of each project based on user's contributions
**Status:** Not Started  
**Planned Approach:**
- Algorithm based on: commit count, lines changed, recency, file complexity
- User can override rankings
- API endpoint to return ranked projects

### 18. ❌ Summarize the top ranked projects
**Status:** Not Started  
**Planned Approach:**
- Use LLM to generate natural language summaries
- Extract key metrics for summary
- API endpoint: POST `/api/projects/summarize`

### 19. ❌ Delete previously generated insights
**Status:** Not Started  
**Requirements:**
- Soft delete or hard delete options
- Ensure shared files across multiple reports remain intact
- API endpoint: DELETE `/api/insights/{id}`
- Cascade delete logic

### 20. ❌ Produce a chronological list of projects
**Status:** Not Started  
**Requirements:**
- Extract project dates from Git history
- Sort by first commit or creation date
- API endpoint: GET `/api/projects/timeline`

### 21. ❌ Produce a chronological list of skills exercised

**Status:** Not Started  
**Requirements:**

- Timeline view of skills used across projects
- Track skill evolution over time
- API endpoint: GET `/api/skills/timeline`

---

## 🏗️ Current Infrastructure

### Backend

- ✅ Django REST Framework API
- ✅ MySQL database with User model
- ✅ File upload and ZIP extraction
- ✅ Git repository analysis
- ✅ Project classification system
- ✅ Authentication (login/register)
- ✅ Docker containerization

### LLM Service

- 🚧 Express.js API on Oracle Cloud VM (exists on `LLM-security` branch)
- 🚧 Ollama hosting llama3.1:8b model (deployed but not integrated)
- 🚧 API key authentication (in separate branch)
- 🚧 Rate limiting (in separate branch)
- ❌ Not merged to main branch yet

### Frontend

- 🚧 Next.js setup (basic structure)
- ❌ Dashboard UI (not started)
- ❌ File upload interface (not started)
- ❌ Project visualization (not started)

### Testing

- ✅ Unit tests for classifiers (6 tests)
- ✅ Integration tests for upload (8 tests)
- ✅ Database model tests (2 tests)
- ✅ User model tests (12 tests)
- ✅ Upload with classifier tests (4 tests)
- **Total:** 32 tests on main branch
- ❌ LLM service tests (exist on `LLM-security` branch only)

---

## 🎯 Next Steps for Milestone 1 Completion

### Priority 1 (Critical)

1. **Frontend consent flow** - User permission UI for LLM usage
2. **Privacy policy** - Document data handling and implications
3. **Configuration storage** - Save user preferences
4. **Skill extraction** - Implement LLM-based or heuristic skill detection
5. **Project timeline extraction** - Parse Git commit dates for duration

### Priority 2 (Important)

6. **Portfolio storage** - Database models for saving portfolios
7. **Project ranking** - Algorithm for importance scoring
8. **Timeline endpoints** - Chronological project and skill views
9. **LLM branch merge** - Integrate LLM service into main

### Priority 3 (Nice to have)

10. **Resume generation** - Export formatted resume items
11. **Project summaries** - LLM-generated descriptions
12. **Delete functionality** - Safe deletion with dependency checks

---

## 📈 Technical Debt & Known Issues

1. **No frontend UI** - Backend API ready but no user interface
2. **Limited error handling** - Need more robust exception handling
3. **No authentication on upload endpoint** - Currently open to all users
4. **No project data persistence** - Analysis results only returned as JSON, not saved to database
5. **Missing database models** - No Project, File, or Portfolio models exist
6. **LLM service not in main** - Deployed on separate branch, needs integration
7. **Project duration not extracted** - Git dates not being parsed yet
8. **Activity type breakdown missing** - Can't distinguish code vs test vs doc contributions
9. **No caching** - Repeated analysis of same files
10. **No async processing** - Large uploads block the request

---

## 🔧 Technology Stack Summary

| Component | Technology | Status |
|-----------|------------|--------|
| Backend API | Django REST Framework | ✅ Deployed |
| Database | MySQL 8.0 | ✅ Running |
| LLM Service | Ollama + Express | 🚧 In separate branch |
| Frontend | Next.js | 🚧 Basic Setup |
| Authentication | Django Auth | ✅ Working |
| Containerization | Docker Compose | ✅ Configured |
| Version Control | Git | ✅ Active |
| Testing | Python unittest | ✅ 32 tests passing |

---

## 📊 Milestone 1 Completion Estimate

- **Target Date:** [Add your target date]
- **Current Progress:** 30% complete (6/20 fully done, 6/20 partial)
- **Estimated Completion:** ~3-4 weeks for remaining critical items
- **Blockers:** 
  - Frontend development (no UI exists)
  - Skill extraction algorithm
  - Portfolio/resume data models
  - LLM branch integration
  - Project timeline extraction

---

## 📝 Notes

**Branch Status:** This report reflects the state of the **main branch only** as of October 30, 2025.

**Feature Branches:**

- `LLM-security` branch contains deployed LLM service (Oracle Cloud VM) with security features
- `project-classifier` branch has been merged to main
- Other features may exist in feature branches not yet merged

**Test Coverage:** 32 tests passing on main branch (test_llm.py exists only on LLM-security branch)

---

**Report Generated:** October 30, 2025  
**Last Updated:** October 30, 2025  
**Branch:** main
