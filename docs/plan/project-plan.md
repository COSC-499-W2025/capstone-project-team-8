# Project Plan Document

## Team Information
- **Team:** Team 8
- **Project:** [Project Name/Title]
- **Date:** [Current Date]
- **Team Members:** 
  - Kyle McLeod
  - Charlie Schwebius
  - Harper Kerstens
  - Jordan Truong
  - Kyle Porter
  - Matin Raoufi

## Project Overview

### Scope
describe the project and the scope

### Usage Scenario
A graduating student or early professional opens the webapp and uploads a folder of their work artifacts. The system scans the uploaded folder and extracts metadata, then analyzes the contents to only return files that they've worked on. The user can then use the dashboard to pick which artifacts to showcase and then export it as a folder containing all their organized work. Employers will be able to access these folders and evaluate the person's skills and growth.

#### Target User Groups
1. **Graduating Students:**
- They want to create a portfolio to show their work for internships, careers, or graduate programs.
- They have a lot of work artifacts from their schooling and want to organize them.

2. **Early Career Professionals:**
- They have been working on personal or career projects.
- They want to track their growth, reflect on past projects, and/or strengthen their portfolio.

### Proposed Solution
talk about technical solution. stack, architecture, etc.

#### Key Features
- **[Feature 1]:**
- **[Feature 2]:** 
- **[Feature 3]:** 

#### Value Proposition
why is our solution better than existing ones.

### Technology Stack
list all the tech we will use and its use case.

#### Frontend
- **Framework/Library:** React (for building reusable UI components and state management)  
- **Styling:** Tailwind CSS (for rapid and responsive UI design)  
- **Additional Tools:** Next.js (for server-side rendering and routing)  

#### Backend
- **Language:** JavaScript/TypeScript  
- **Framework:** Node.js with Express (for API handling and server logic)  
- **Database:** PostgreSQL (for storing metadata, user accounts, and portfolio configurations)  
- **Additional Services:** Cloud Storage (AWS S3 or equivalent for file uploads and management)  

#### Development & Deployment
- **Version Control:** Git, GitHub  
- **Testing Framework:** Jest + React Testing Library (unit and integration testing for frontend and backend)  
- **Deployment Platform:** Vercel (for frontend) and Render/Heroku (for backend)  

## Functional Requirements

### Core Requirements
1. **[Requirement 1]** - title
   - **Description:** add

2. **[Requirement 2]** - title
   - **Description:** add

add more here

## Requirements Verification

### Testing Framework
**Selected Framework:** Jest with React Testing Library  
**Justification:** Jest is widely used with JavaScript/TypeScript projects, supports fast unit and integration testing, and works seamlessly with both Node.js and React. React Testing Library complements it by enabling testing of UI behavior rather than implementation details. This ensures high reliability and maintainability.  

### Test Cases

#### 1 - File Upload Handling
- **Test Case 1:**
  - **Input:** A folder containing multiple files of different types (e.g., `.pdf`, `.docx`, `.png`)  
  - **Expected Output:** The system successfully uploads the folder and stores metadata for each file.  
  - **Test Type:** Backend  
  - **Automation:** Automated Jest test with mock file uploads  

#### 2 - Metadata Extraction
- **Test Case 1:**
  - **Input:** A `.pdf` and `.docx` file uploaded by the user  
  - **Expected Output:** Extracted metadata (file name, size, date modified, type) stored in the database  
  - **Test Type:** Backend  
  - **Automation:** Automated Jest test simulating file parsing  

#### 3 - Dashboard Display
- **Test Case 1:**
  - **Input:** User has uploaded three valid files  
  - **Expected Output:** Dashboard displays all three files with metadata and selection options  
  - **Test Type:** Frontend  
  - **Automation:** React Testing Library rendering test  

#### 4 - Export Portfolio
- **Test Case 1:**
  - **Input:** User selects two files to showcase and clicks “Export”  
  - **Expected Output:** System generates a downloadable folder with only the selected files, organized properly  
  - **Test Type:** Full-stack (frontend trigger, backend processing)  
  - **Automation:** Integration test with mocked backend and frontend action  

## Proposed Workload Distribution

### Team Member Assignments

#### [Member 1 Name]
- **Primary Requirements:** list the ones they take on
- **Secondary Requirements:** list
- **Difficulty Balance:** ensure a mix of easy, medium, and hard tasks

#### [Member 2 Name]
- **Primary Requirements:** list the ones they take on
- **Secondary Requirements:** list
- **Difficulty Balance:** ensure a mix of easy, medium, and hard tasks

do for all members

## Timeline & Milestones

### Milestone 1: [Date]
- list key deliverables and requirements to be completed

### Milestone 2: [Date]
- list key deliverables and requirements to be completed

### Final Delivery: [Date]
- project to be completed

## Conclusion
summarize the plan and express confidence in the team's ability to deliver the project successfully.