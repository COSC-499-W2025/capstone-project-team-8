# Kyle McLeod's Weekly Logs
## Week 3 September 15-21
<img width="624" height="358" alt="Screenshot 2025-09-21 144528" src="https://github.com/user-attachments/assets/abef3302-eb64-4093-b540-9c8f9dc87dd8" />

- Created list of functional and non-functional requirements with team
- Revised requirement list after feedback
- Discussed possible tech stack with team
- File structure organizationin GitHub repository

## Week 4 September 22-28
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/a6999f11-c3db-4aa2-9b07-e669e74e2122" />

- Put together the project proposal template
- Worked on a system architecture diagram with the team
- Revised the diagram based on other teams suggestions
- Helped plan the stack we will use

## Week 5 September 29 - October 5
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/239e9fcd-13e5-4555-b5e4-a13b394b003d" />

- Helped create level 0 and level 1 diagrams
- Got feedback from other groups and revised the diagrams accordingly
- Created and organized a Kanban board so we can keep track of the issues we create
- Researched on other companies that provide a solution on the project task (this can be used to understand the system requirements more and allow us to areas where our project could offer a more effective or innovative approach)

## Week 6 October 6-10
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/7fca0375-5f18-4cc4-b697-c69d39765a72" />

- Installed Next.js to a front end folder (we probably won't be using this until miletsone 2 but it is good to see the whole project folder setup)
- Documented on how to start the front end server
- Created issues on our Kanban board and assigned tasks to teammates
- Reviewed Harper and Charlie's pull requests
- Suggested revisions on the backend folder structure
- Read Django docs to learn how to create API routes

## Week 7 October 13-17
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/023f0d28-72e4-4251-8409-b422113aea29" />

- created a document proposing a plan for our AI analysis layer
- compared multiple cloud hosting platforms for AI hosting
- the document has 3 different ooptions we can choose and we will further discuss the final choice in our next team meeting
- created issues on our kanban board
- reviewed harpers pull request
- reviewed matins pull request
- updated main readme file

## Week 8 October 20-24
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/d7c0fedd-f40c-41e3-85f2-eca0af9093c7" />

- designed and created an AI layer that will play a crucial role in getting insights on files
- scalable and easily portable so we can host it on any cloud host
- chose a cloud host provider and am now going to work on deploying the model so we can use a powerful model for testing
- did weekly logs
- reviewed harpers pull request on file classification
- reviewed matins pull request on database configuration
- populated kanban board with more tasks for next week

## Week 9 October 27-31
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/6ae665ff-98b2-41e9-8bec-fb3b6c31b9c0" />

- hosted the AI model on a Oracle cloud VM
- allocated CPU, Ram & memory
- tested the AI model
- protected endpoints from any attacks since this API is public facing
- added rate limiting
- added API key protection to endpoint
- VM networking
- reviewed teammates PR's
- tested teammates code
- collaborated with teammates to discuss JWT token implementation
- picked up issues on Kanaban dashboard

It was difficult to find a cloud hosting provider that offers GPU’s while on a free trial or student account. For now, our AI layer is hosted on a 8 core CPU, 64GB ram and 200GB machine. This should be fine for testing purposes, but if we ever deployed this application, scaling would be required. Since our AI layer is modular, it can be easily ported to a different powerful machine.

What went well this week was testing how flexible the AI layer is that I built. This model can be tailored for almost any use case. I found a bunch of open source prompts that will help with code analysis and we can utilize this on the model if the user agrees to AI processing.

Next week I’m going to work on file specific analysis and starting the foundation of a resume builder.

## Week 10 November 3-7
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/b1693052-b382-4e35-a5be-7e976d5f2ff8" />

- added file upload capapbilities to LLM layer https://github.com/COSC-499-W2025/capstone-project-team-8/pull/125 
- added an LLM prompt library that allows us to attach analysis specific prompts to files https://github.com/COSC-499-W2025/capstone-project-team-8/pull/127
- dockerized the LLM for easy portability on any machine (this helps us a lot since we will be rotating cloud providers to take advantages of free credits during development) https://github.com/COSC-499-W2025/capstone-project-team-8/pull/129
- reviewed team PR's
- discussed plans or AI integration

This week I made a lot of progress on our AI layer and it is almost ready to be connected to our extraction & analysis pipeline. I struggled deploying the updated code to our VM since it wasn't using a docker container before. Now that the docker container is set, I don't need to worry about dependencies and the struggle of outdated versions and such.

I didn't get to finish the file specific analysis Issue #115, but I hope to integrate my new AI file processing layer into this feature next week.

## Week 11 & 12 November 10-21
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/6112f39d-b5b9-41e9-93ba-2310e143e01e" />

This week:
- refactored analysis and classifiers logic PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/143 ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/142
- a lot of our classifiers and analysis files served multiple purposes before my PR this week, this PR split up the logic into mutliple simpler files to make development easier and reduce merge conflicts we might have in the future
- tested functionality after refactor
- after I refactored the analysis and classifiers logic, Matin branched off my work and started the refactor on the uploadFolderView.py file, which was a file with 11 responsibilities
- our whole codebase is now much simpler
- also worked on structing database to save projects and information
- savedkey information to a database PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/156 ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/145

What went well:
- worked with Matin efficiently in refactoring
- no merge conflicts while implementing the refactor since we split up work in seprate non conflicting parts
- make some progress on how to structure database and will propose to the team next week

What went wrong:
- after testing the AI server for this week, it just isn't quite powerful enough
- requests take 30s - 2m depending on length
- this might be fine for testing, but I'm going to look into configuring VM specs better or finding other hosts that offer better free plans

Next week:
- based on information saved, configure a process for AI resume builder https://github.com/COSC-499-W2025/capstone-project-team-8/issues/103

Reflection:
This week I learned that it's important to keep a clean code structure from the start, since having the messy code might have delayed our progress by a little bit. Now that we have a refactored codebase, we are ready to implement some more complex features.

## Week 13 November 24-28
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/94a3dc69-60d2-49e5-ba47-96d5a6bfda10" />

This week:
- bug fix on fixing our file analyzer still scanning dependency folder PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/172 ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/137
- LLM microservice doc updates PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/177
- migrated AI to a new host and made big performance improvements PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/179 ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/176
- created user API endpoints PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/180 ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/169
- setup and contributed to slides for our presentation
- LLM test patch PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/192
- reviewed matins code PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/186
- reviewed jordans code PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/193
- reviewed harpers code PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/178

What went well:
- made a lot of progress with AI, our responses are much faster now and we can start integrating this in our analysis pipeline
- our codebase is staying clean since our refactor

What went wrong:
- our new AI is from Azure foundry which is an AI platform that enables developers to quickly made AI agents
- I'm not 100% sure if data is kept or used for training with this API
- we will use this AI for development and if we need to worry about security/privacy later, we can deploy our AI microservice I programmed

Next week:
- present our project
- prepare for milestone 2

Reflection:
We have made a lot of progress since our last week. Ever since we got the refactor done and started using our database, our development has been a lot smoother. We will present our project and prepare for milestone 2. I'm happy with the progress we have made for the first term.

## Week 14 December 1-5
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/460e928e-b2d2-42f0-b723-a0fa635afdd9" />

This week:
- bug fix on main not having JSON bullet points ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/203 PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/204
- saved bullet points to database ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/202 PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/207
- github workflow modification so main runs tests ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/206 PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/205
- video walkthrough demo (10 mins)
- team contract

What went well:
- video demo software is working great for recording walkthroughs
- reviewed teammates PR's and provided feedback
- lots of collaboration in our team discord

What went wrong:
- we had a brief problem with merging all our PR's last week so our main branch was missing features
- we resolved the issues this week and made sure main is up to date with all features

Next week:
- winter break
- would be nice to do some design mocks next week to get an idea of how the front end will look & the requirements

Reflection:
This is the final week of the semester before winter break and we have successfully completed all milestone tasks. For the next term, we will refine our analysis and make sure we are getting accurate insights.

## Week 15 January 5-9
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/7134bfa8-1730-4977-99ae-14a4faf64312" />

This week:
- latex resume generator PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/216 ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/215
- reviewed Harpers PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/211 ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/210
- reviewed harpers PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/214 ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/213

What went well:
- resume generator is sucvcessfully fetching information from our analyzers which is stored in the database
- harpers pr now gives us more information on what files were committed by who
  
What went wrong:
- we were notified that our milestone #1 had some missing requirements
- we will work on implementing the missing requirements in the following weeks
  
Next week:
- additional fields in the resume generator
- save contribution metrics to database
- work on adding missing requirements from milestone 1
  
Reflection:
Our team is going to think more about how the user will interact with our system and implement any missing requirements from milestone 1. After that, we are going to implement the milestone 2 requirements. A lot of the milestone 2 requirements will build off of the core components we built during the last few months, so development should feel a little more straightforward this term.
