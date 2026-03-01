# Kyle McLeod's Weekly Logs
## Weekly Logs Index
### Term 1
- [Week 3 (Sept 15–21)](#week-3-september-15-21)
- [Week 4 (Sept 22–28)](#week-4-september-22-28)
- [Week 5 (Sept 29–Oct 5)](#week-5-september-29---october-5)
- [Week 6 (Oct 6–10)](#week-6-october-6-10)
- [Week 7 (Oct 13–17)](#week-7-october-13-17)
- [Week 8 (Oct 20–24)](#week-8-october-20-24)
- [Week 9 (Oct 27–31)](#week-9-october-27-31)
- [Week 10 (Nov 3–7)](#week-10-november-3-7)
- [Week 11 & 12 (Nov 10–21)](#week-11--12-november-10-21)
- [Week 13 (Nov 24–28)](#week-13-november-24-28)
- [Week 14 (Dec 1–5)](#week-14-december-1-5)
### Term 2
- [T2 Week 1 (Jan 5–9)](#week-15-january-5-9)
- [T2 Week 2 (Jan 12–16)](#week-16-january-12-16)
- [T2 Week 3 (Jan 19-23)](#week-17-january-19-23)
- [T2 Week 4-5 (Jan 26-Feb 6)](#week-18--19-january-26---february-6)
- [T2 Week 6-7-8 (Feb 9-27)](#week-20--21--22-february-9-27)


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
- 
## Week 16 January 12-16
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/7134bfa8-1730-4977-99ae-14a4faf64312" />

This week:
- implemented bugfix on API error PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/241
- backend byte size and char count bugfix PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/254
- quick UI styling change PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/252
- reviewed Matins PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/244
- reviewed Harpers PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/238

What went well:
- prepped for peer evals
- got a bare ones user interface to interact with our API's we created

What went wrong:
- a few bugs with our backend
- our API endpoints list are starting to pickup and we need a solution to track them all. we are thinking of starting documention for API's so we can all stay on the same page and not create overlapping code
  
Next week:
- fix backend bugs such as dates not returning properly
- adjust accuracy of our system and make sure classification login and analyzer logic is returning proper results
- work on getting the resume system done
  
Reflection:
We now have a UI that is connected to our Django backend. This will help plan out future backend features since we will be able to find shortcomings in our app. I feel like we were slightly bottlenecked in which features to work on since we didn't have an idea of how the user would actually interact with the system. But now since we have a quick UI to see, I can already see a lot of bugs and such that our backend has. We can include these tasks in our next week.

## Week 17 January 19-23
(TODO) - img

This week:
- created a comprehensive API documentation for our backend endpoints PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/257 ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/256
- refactored serializer logic into multiple small files PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/265 ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/262
- fixed migration bugs with Matin PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/258 ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/259
- quick bug fix again with PR last week not merged properly PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/269
- reviewed matins refactor PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/263
- review harpers PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/264

What went well:
- prepped for heuristic evaluations
- automatic api docs can be used for executing api commands for evaluation and also keep the team updated with every endpoint we have and the values returned
  
What went wrong:
- more bugs this week with migration issues, we need to start merging PR's more carefully

Next week:
- since our Azure AI free trial expired, we will need another group member to make an account and connect it
- fix bugs with dates not shwoing correctly, some values NULL on return still
- refine accuracy on classifiers
  
Reflection:
We now have a full API docs page and users are able to interact with the APIs listed. This can be used for our heuristic evaluations on monday since our UI is not complete. The bulk of our features are done, and we will be spending time on refining the accuracy and making sure the data that comes in and out of our system is feasible.


## Week 18 & 19 January 26 - February 6
<img width="610" height="319" alt="image" src="https://github.com/user-attachments/assets/b1fa5487-6b3e-4114-b8e6-c967714f153c" />

This week:
- created a terminal interface for our backend PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/278
- redesign login, signup, landing PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/279
- review harpers PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/275
- review matins PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/281
- quick review jordans PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/282
  
What went well:
- we started integrating a UI to our backend
- system is working as expected with our UI
  
What went wrong:
- still numerous bugs throughout our system
- accuracy of system still not well known since we havent tested on lots of test files/folders

Next week:
- work on analysis for less coding type projects and more other subjects
- continue to refine accuracy and test system with new types of data
- refactor any more messy components
  
Reflection:
Our team is working on refining our system and getting things looking good. We still have a couple requirements to check off for milestone 2, but I am happy with our progress. Some parts of our codebase are messy still, but we will continue to refactor to make it easier to contribute to.

## Week 20 & 21 & 22 February 9 - 27

This week:
- made bugfix PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/286 ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/285
- ui PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/288 ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/287
- resume bugfix PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/290 ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/289
- auth redirect bugfix PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/301 ISSUE: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/300
- show evaluated percentages on dashboard PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/302
- reviewed matins PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/293
- reviewed harpers PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/294
- reviewed harpers PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/295
  
What went well:
  
What went wrong:

Next week:
  
Reflection:


