# T8BG Team Log
|Username|Student Name|
|-|-|
|kylekmcleod|Kyle McLeod|
|jordany78|Jordan Truong|
|cschwebi|Charlie Schwebius|
|matin0014|Matin Raoufi|
|Porter-K|Kyle Porter|
|harperkerstens|Harper Kerstens|

## Week 12: Nov 16 - 22

### Our Goals for this week:
  Our goals for this week were to make progress towards finalizing things for Milestone 1. This included more database integration with uploaded projects, improving our analysis engine, and finishing off any unfinished areas of development for the analyzer. Alongside some minor bug fixes our focus was mainly poloshing off some rough edges that needed attention before the submission. The database is the last major step for the project in regards to this milestone so this was also of key focus for us this week.


### Reflection:
  This week development went very smoothly with little to no blockers. The team worked well and collaborated nicely to assist each other in areas where needed. The database now saving projects was massive for us this week as well, now we are able to store results from the analysis and we will be able to hopefully have massive performance increases as a result from this. We are feeling good about our progress towards Milestone 1 and are excited to see the final product come together.


### What went well:
  Development was definitely the highlight for our group this week. Each of us made solid progress this week and we were able to get a lot done. Our analyzer is nearly complete which allows us to focus on the final steps for the project in this last week.


### What didn't go well:
  There were minimal issues this week, however we did run into some small bugs with saving into the database and the data models. These have been resolved for the most part but will need some final polishing before Milestone 1.


### Burn Up Chart




### Completed Tasks

| Task | Assigned To | Issue # | Pull Request |
|------|-------------|---------|--------------|
| | |  |  |
| | |    |  |
| | |      |  |
|  | |  |  |
|  |  |     |  |
|  |   |      |  |
|   |  | |  |

### In Progress Tasks

| Task | Assigned To | Issue # |
|------|-------------|---------|
|      |             |         |
|      |             |         |
|      |             |         |

### Next Weeks Plan Towards Milestone 1 



### Test Report




## Week 10: Nov 2 - 9

### Our Goals for this week:
Our goal for this week was to deepen our analysis of uploaded files and progress towards AI integration. For uploaded files, we aimed to enhance our file analyzer to read text from uploaded content documents as well as discover tech stacks and languages used in coding projects. This work being done is pivotal to both a non AI and AI based analysis of user projects. The more information we can extract from uploaded files, the better our analysis engine will perform. Another goal for this week was to analyze deeper the .git file in a detected repository, trying to distinguish user contributions is a key step towards milestone 1.


### Reflection:
This weeks development went smoothly with minimal hitches. The team collaborated well to implement new features and make decisions for our projects direcetion. As we dive deepper into content analysis the project is starting to take shape and we are excited to see progress. The teams focus shifting forward is to better understand the read content of uploaded files this week was focused on accessing the files now we have to take it a step further and understand what is in those files. AI will help with this but determining a non AI approach is also important for our project.


### What went well:
Development was smooth this week with minimal blockers. We were able to stay on track with our goals and each make strong team and individual contributions. Our implemented features are being strengthened as well being able to deeper understand user's uploaded files.


### What didn't go well:
As we work in our file uploader component the file is begining to grow in size and complexity. We must begin to make decisions on how to modularize and structure our code to ensure further development is smooth and efficient. Small refactoring was done this week but it should become a larger focus moving forward.


### Burn Up Chart

<img width="1821" height="1039" alt="image" src="https://github.com/user-attachments/assets/19bce1df-2f9f-4327-8bb4-43fb518b4d85" />



### Completed Tasks

| Task | Assigned To | Issue # |
|------|-------------|---------|
|detect coding languages and frameworks|cschwebi| https://github.com/COSC-499-W2025/capstone-project-team-8/issues/77 |
|User Consent Features | harperkerstens | https://github.com/COSC-499-W2025/capstone-project-team-8/issues/113,    https://github.com/COSC-499-W2025/capstone-project-team-8/issues/114   |
| Reading Text from uploaded Documents |harperkerstens| https://github.com/COSC-499-W2025/capstone-project-team-8/issues/105      |
| LLM File Upload | kylekmcleod |  https://github.com/COSC-499-W2025/capstone-project-team-8/issues/124  |
| Dockerize LLM and Updated VM  | kylekmcleod  |  https://github.com/COSC-499-W2025/capstone-project-team-8/issues/126     |
| Filter project by user contributions | jordany78  | https://github.com/COSC-499-W2025/capstone-project-team-8/issues/60     |
| Chronological git project list   | matin0014 | https://github.com/COSC-499-W2025/capstone-project-team-8/issues/72 |

### In Progress Tasks

| Task | Assigned To | Issue # |
|------|-------------|---------|
|      |             |         |
|      |             |         |
|      |             |         |

### Next Weeks Plan Towards Milestone 1 
Looking forwards towards Milestone 1 our key objectives are content analysis based, specifically:,
5. Have alternative analyses in place if sending data to an external service is not permitted
9. Extrapolate individual contributions for a given collaboration project 
10. Extract key contribution metrics in a project, displaying information about the duration of the project and activity type contribution frequency (e.g., code vs test vs design vs document), and other important information 
11. Extract key skills from a given project 


### Test Report


## Week 9: Oct 25 - 29

### Our Goals for this week:

Our goal for this week was:
  - Setup LLM cloud server #70 #83 
  - Implement JWT based auth #92
  - Refactor login view to return JSON #73 
  - Refactor JSON output for queries #76 
  - Find user contributions in .git files #62 
  - Fix UploadFolderView file #88
  - Create Milestone 1 progress report #90
  - Implement feature to detect projects without a repository #72

  ### Reflection:
  This week was our first encounter with system breaking bugs. Expecting development to continue as it has this threw a curve ball into our plans for the week. However, the team came together to resolve these issues and use the opportunity to refactor and modularize our code. Overall, we are still happy with our progress being able to make significant developments despite the setbacks.

  ### What went well:
  - Successfully set up the LLM cloud server
  - JWT based authentication successfully protects all our routes
  - Refactored lots of code to ensure future development is smoother and more modular

  ### What didn't go well:
  - Some team members had trouble setting up the cloud server locally
  - Unexpected bugs and errors forced us to refactor code multiple times
  - Some tasks took longer than expected, leading to minor delays

### Burn Up Chart

<img width="1044" height="541" alt="image" src="https://github.com/user-attachments/assets/be94c3bf-eb6a-450e-8c12-9f979c6b7e2d" />


### Completed Tasks

| Task | Assigned To | Issue # |
|------|-------------|---------|
| Host LLM layer on cloud | kylemcleod | [COSC-499-W2025/capstone-project-team-8#70](https://github.com/COSC-499-W2025/capstone-project-team-8/issues/70) |
| Implement JWT based Auth | matin0014 | [COSC-499-W2025/capstone-project-team-8#92](https://github.com/COSC-499-W2025/capstone-project-team-8/issues/92) |
| Refactor login view to return JSON | matin0014 | [COSC-499-W2025/capstone-project-team-8#73](https://github.com/COSC-499-W2025/capstone-project-team-8/issues/73) |
| Refactor JSON output for queries | cschwebi | [COSC-499-W2025/capstone-project-team-8#76](https://github.com/COSC-499-W2025/capstone-project-team-8/issues/76) |
| Find user contributions in .git files | jordany78 | [COSC-499-W2025/capstone-project-team-8#62](https://github.com/COSC-499-W2025/capstone-project-team-8/issues/62) |
| Fix UploadFolderView file | harperkerstens | [COSC-499-W2025/capstone-project-team-8#88](https://github.com/COSC-499-W2025/capstone-project-team-8/issues/88) |

### In Progress Tasks

| Task | Assigned To | Issue # |
|------|-------------|---------|
| Create Milestone 1 progress report | matin0014 | [COSC-499-W2025/capstone-project-team-8#90](https://github.com/COSC-499-W2025/capstone-project-team-8/issues/90) |
| Implement feature to detect projects without a repository (Under review) | Porter-K | [COSC-499-W2025/capstone-project-team-8#72](https://github.com/COSC-499-W2025/capstone-project-team-8/issues/72) |
|      |             |         |

### Test Report
<img width="794" height="383" alt="image" src="https://github.com/user-attachments/assets/dd645cf4-ee22-488b-8e80-b1d9dd9e0155" />

## Week 8: Oct 20 - 24

#### This week we:
- Added additional functionality to our file analyzer
- Implemented a custom user model for our database
- Confirmed the plan for our AI host
- Setup a portable AI/LLM layer which we will host on the cloud
- Authentication setup
- Reviewed PR's and provided feedback
- Wrote tests for our new analysis functions

### Reflection:
Our team has made a lot of progress on our extraction and analysis process. Our extraction layer is close to being complete and we will be forwarding the data to our analysis engine. Our team collaboration has been great and we have been answering eachothers questions in our group Discord channel. So far, we have had no problems as a team, and we have our tasks set for next week.

  ### What went well:
- Successful implementation of the file analyzer
- Effective team collaboration and communication
- Progress on the AI host plan

  ### What didn't go well:
- Some delays in the implementation timeline
- Minor issues with the database setup

Our Week 8 Milestone:
<img width="1070" height="812" alt="image" src="https://github.com/user-attachments/assets/2c749fe1-3957-42b4-9571-53a00dec52b6" />

Burn Up Chart:
<img width="1070" height="812" alt="image" src="https://github.com/user-attachments/assets/2cc8ec9f-d78e-47d2-aeac-bff36cb6b282" />


## Week 7: Oct 13 - 17

#### This week we:
- Dockerized frontend
- Dockerized backend
- Got a MySQL local database running and dockerized it
- Implemented a simple file type analyzer/classifier - this will be one of many layers of processing in our analysis pipeline
- Wrote tests for our file classifier
- Wrote tests to confirm the database connection is working
- Wrote a document on our AI/LLM server hosting plan
- Refactored our codebase
- Created issues in our kanban dashboard for next weeks sprint

Overall this was a productive week and we are just finalizing our project setup before we make major changes and updates. We will be discussing the AI model plan during next week and once that is complete, we will be working on core functionality. Our plan is to separate the file processing into multiple small layers, and this will allow us to assign chunks to each teammate independently.
  
## Week 6: Oct 6 - 12

#### This week we:
- Revised diagrams and added links to README.md file
- Added a simple Docker container setup we can build on to
- Set up Django backend framework
- Set up Next.js frontend framework
- Set up and familiarized ourselves with the expected pull request process (PR template, commenting, etc)
- Reviewed PR's and provided feedback

### Burnup Chart
<img width="1727" height="882" alt="image" src="https://github.com/user-attachments/assets/b9141939-d185-4a80-bbc2-277b077223c3" />


## Week 5: Sept 29 - Oct 5

This week we created our level 0 and level 1 DFD and discussed with multiple teams on what went well and what could've been done better.
- We were able to make our diagrams fairly quick with little confusion
- We could've reviewed our diagrams a bit more, so we could answer the other teams questions better

Next week, we will finalize our requirements/system design architecture, and allocate our work load.

## Week 4: Sept 22 - 28

- Created system architecture diagram
- Created project proposal

## Week 3: Sept 15 - 21

- Created requirements document
