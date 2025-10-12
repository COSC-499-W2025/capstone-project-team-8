# Work Breakdown Structure (WBS)


1. Project Planning & Setup (Sept- Oct)
	- 1.1 Learn guidelines and create requirements
		- 1.1.1 Review and agree on project guidelines
		- 1.1.2 Produce requirements document
        - 1.1.3 Create diagrams (DFD, SAD)
	- 1.2 Choose technology stack
		- 1.2.1 Select frontend and backend frameworks
		- 1.2.2 Define PR and weekly log process
	- 1.3 Repository & onboarding
		- 1.3.1 Initialize repo and basic folder structure
		- 1.3.2 Create initial README and revise diagrams
2. File Upload & Scanning (Oct- Nov)
	- 2.1 Frontend: Folder upload UI
		- 2.1.1 Implement folder selection and upload
		- 2.1.2 Give feedback on upload process
		- 2.1.3 Request user permission before accessing files
	- 2.2 Backend: Upload handling & storage
		- 2.2.1 Create API route for uploads
		- 2.2.2 Integrate storage (SQLite)
		- 2.2.3 add error handling and retry mechanisms
	- 2.3 Metadata extraction
		- 2.3.1 Extract file name, size, timestamps, type
		- 2.3.2 Persist metadata to database
		- 2.3.3 Write unit tests for extraction logic (TDD)

3. Artifact Categorization & Analysis Engine (Nov- Dec)
	- 3.1 File classification
		- 3.1.1 Define categories
		- 3.1.2 Implement classification pipeline
	- 3.2 Code metrics and LOC analysis
		- 3.2.1 Count lines per language
		- 3.2.2 Detect dominant languages per project
	- 3.3 Relevance scoring and ranking
		- 3.3.1 Design scoring heuristics (recency, edits, file type, contributions)
		- 3.3.2 Implement ranking system (Scoring, Dating, etc.)

4. Dashboard & Visualization Development (January)
    - 4.1 Basic Functional Implementation
        - 4.1.1 Implement File Upload
        - 4.1.2 Implement file analysis and return results
	- 4.2 Core dashboard components
		- 4.2.1 Implement dashboard visualization
		- 4.1.2 Implement filters, search, and sorting
	- 4.3 Frontend tests (TDD)
		- 4.3.1 Component unit tests
		- 4.3.2 Integration tests for dashboard flow

5. Folder Export & Report Features (February)
 	- 5.1 Server-side report generation
 		- 5.1.1 Generate project dashboard screenshots (PNG) or printable HTML/PDF
 		- 5.1.2 Produce AI analysis report summarizing project and user contributions (HTML/PDF)
 		- 5.1.3 Store report artifacts and track generation status
 	- 5.2 Delivery and access
 		- 5.2.1 Provide links to reports
 		- 5.2.2 Support email or in-app delivery of reports

6. Refinement & Advanced Features (March)
	- 6.1 Security and privacy hardening
		- 6.1.1 Implement rate limiting and permission prompts
		- 6.1.2 Security testing (TDD)
	- 6.2 Cross-platform responsiveness
		- 6.2.1 Mobile and tablet layout adjustments
		- 6.2.2 Accessibility improvements

7. Final Testing & Delivery (April)
	- 7.1 Review and Finalize testing
		- 7.1.1 Coverage and code review
		- 7.1.2 Run test plan and patch bugs
	- 7.2 Documentation and deployment
		- 7.2.1 Final README, documentation, user guides
		- 7.2.2 Deploy and configure environment




