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
- **Automated Artifact Organization:** Automatically identifies relevant work artifacts from uploaded folders.  
- **Metadata Extraction and Insight:** Extracts metadata such as file type, size, creation date, and optionally project details.  
- **Interactive Dashboard:** Allows users to view, filter, select, and categorize files for their portfolio.  
- **Exportable Portfolio Package:** Creates a structured downloadable folder (`.zip`) ready to share.  
- **Cross-Platform Access:** Works on desktop and mobile browsers.  
- **Privacy and Security Controls:** Users control which files are included and how data is accessed.  

#### Value Proposition
Our solution saves time by automating artifact organization, tracks project growth with metadata insights, offers an intuitive dashboard for curation, enables flexible export options for offline sharing, and ensures secure, private handling of user files—features that many existing portfolio tools lack.  

### Technology Stack

#### Frontend
- **Framework/Library:** React (for building reusable UI components and state management)  
- **Styling:** Tailwind CSS (for rapid and responsive UI design)  
- **Additional Tools:** Next.js (for server-side rendering and routing)

#### Backend
- **Language:** JavaScript 
- **Framework:** Node.js with Next.js API routes (for API handling and server logic)  
- **Database:** MySQL (for storing metadata, user accounts, and portfolio configurations)
- **Authentication:** NextAuth (for secure authentication)
- **Additional Services:** Cloud Storage (AWS S3 or equivalent for file uploads and management)  

#### Development & Deployment
- **Version Control:** Git, GitHub  
- **Testing Framework:** Jest + React Testing Library (unit and integration testing for frontend and backend)  
- **Deployment Platform:** Vercel 

## Functional Requirements

### Core Requirements

#### File Analysis & Processing
- The system shall extract metadata from working files.  
- The system shall analyze content of applicable working files.  
- The system shall analyze the number of lines of code written in each language and give insights on the code that has been written.  
- The system shall be able to use the blame function of version control systems to see what was done by the user.  

#### Reporting & Organization
- The system shall produce a detailed report on the projects that were uploaded and present them on the dashboard.  
- The system shall sort projects based on their estimated detail and content.  

#### User Interaction & Control
- The user shall be able to create custom lists based on projects found in the system.  
- The user will be able to filter what type of work to find before searching.  
- The system shall ask for permission before accessing any files.  

### Non-Functional Requirements

#### Performance
- The system shall be able to handle multiple file uploads at once.  
- The user dashboard shall load quickly and provide visual feedback if data is loading.  

#### Security & Privacy
- User information shall be kept private and files will only be scanned if the user agrees.  
- The API endpoints shall have rate limiting to protect against malicious use.  
- Any storage buckets shall have appropriate row level security.  
- The system shall protect against common web application attacks (SQL injection, XSS).  
- The system shall enforce proper user authentication.  
- The system shall encrypt all data in transit with HTTPS.  

#### Reliability & Availability
- There shall be no data loss when parsing the files and shall handle corrupted or broken files.  
- The server shall have 99.9% uptime.  
- The system shall regularly perform database backups in case of data loss.  

#### Usability
- The user interface shall work on all screen sizes (mobile, desktop, and tablet).  

#### Portability
- The system shall run on multiple operating systems.  

## Requirements Verification

### Testing Framework
**Selected Framework:** Jest with React Testing Library  
**Justification:** Jest is widely used with JavaScript/TypeScript projects, supports fast unit and integration testing, and works seamlessly with both Node.js and React. React Testing Library complements it by enabling testing of UI behavior rather than implementation details.  

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
