
September 15-21

<img width="1069" height="622" alt="image" src="https://github.com/user-attachments/assets/3ebfb261-388d-4c7e-a261-48bf1b64e3c2" />

- Work with team to create functional and non functional requirements
- Discussed with other groups about their ideas with the project
- Helped organize the structure of requirements document

September 22-28

<img width="1087" height="624" alt="image" src="https://github.com/user-attachments/assets/9f56a55c-d0f2-421a-af64-4851ca4f6b85" />

- Worked on system architecture diagram with team
- Added to project proposal
- Reviewed other teams suggestion with group
- Discussed tech stack with group

September 29 - Oct 5


<img width="1090" height="637" alt="image" src="https://github.com/user-attachments/assets/f82c3e9c-3457-4514-93be-cc2e7545ca86" />

- helped make the level 0 DFD & helped with level 1 DFD
- Reviewed other groups DFD's
- Reviewed feedback from other groups with our group

Oct 6 - Oct 12

<img width="1079" height="633" alt="image" src="https://github.com/user-attachments/assets/4c82df6e-f3df-48c5-abe7-9bfca3c40b4f" />

- Learned about DJango framework
- Reviewed pull requests
- Reviewed docker
- Discussed database tech with team
- Provided feedback on pull requests

Oct 13 - Oct 19
<img width="1091" height="644" alt="image" src="https://github.com/user-attachments/assets/7edc2495-59ae-495a-896e-c1226016aedb" />

- Setup a local MySQL database and dockerized it (issue #40 & #39)
- Reviewed pull requests
- Tested my own and teammates code
- Documented database setup and pull requested for peer review
- Things that didn't go well was trying to figure out if we want our database to be hosted locally or not and deciding on relational or non-relational ultimately I tried to stay patient so
  I can have have input from everyone before pulling the trigger on a local MySQL setup
- Things that went well were testing teammate code and reviewing PR's the PR template makes it very easy to review and teammates provide thorough instructions. Setting up the database also went smoothly due to prior
  experience from Cosc 304 coming in handy

- Next I want to work on creating a User model to store users
  
Oct 20 - Oct 26
<img width="1247" height="649" alt="image" src="https://github.com/user-attachments/assets/8b20c376-7e95-44fd-9e21-f3f4984cb17c" />

- Discussed Potential AI integration with group
- Reviewed pull requests
- Tested teammates code
- Tested my own code
- Setup user model for database (issue #61)
- Created several tests
- Pull requested and documented my work

- Things that were difficult were figuring out what type of data for the user we want to store, I imagine we will end up revisiting this in the future
- Things that went well was reviewing PR's and working with the current auth that Kyle Porter had setup to create the user model
- I want to step away from the database a little bit next and work on using web tokens for auth next and see where we are at regarding the milestone




Oct 27 - Nov 2
<img width="1089" height="625" alt="image" src="https://github.com/user-attachments/assets/1fb05ffc-b8e5-4757-9a1e-2e73b95770b7" />

- I worked on a progress report for milestone 1
- Tested my own code
- Tested teammates code
- Implemented JWT authentication for our backend to protect API routes (issue #92)
- Refactored login to output JSON instead of HTML (issue #73)
- Reviewed Pull Requests

- Things that were difficult was implementing the token system broke some tests we had so we need refactor those because the api routes those tests access cant be accessed with out proper authentication now.
  Setting up Ollama on my computer was also difficult to work with Kyle's LLM setup to test his PR
- Things that went well was testing the authentication I implemented with postman, my teammates also said my PR contained thorough instructions to test the features
- Next I want to move more towards data extraction from an input and order the projects in a chornological list from an input

Nov 3 - Nov 9

<img width="1083" height="647" alt="image" src="https://github.com/user-attachments/assets/81d7088c-092a-4bef-9ae7-ff6c71f8a98e" />

- I worked on a feature that orders the list of projects in .git by chronological order based on first commit issue #72
- I tested my teammates code
- I tested my own code
- I reviewed pull requests

- What went well: TDD approach worked perfectly - all tests passed, chronological ordering by git timestamps implemented cleanly, and the merge conflict was straightforward to resolve.

- What didn't go well: Manual testing was initially slow due to node_modules bloat, and had to add temporary directory filtering as a workaround instead of a proper solution.

- Next I want to finish the need for ordering by chronological order by implementing a feature that checks non git projects, I am splitting this up into seperate issues to be easier to manage

Nov 10 - 23 Reading week bonus Week 11 & 12

<img width="1081" height="638" alt="image" src="https://github.com/user-attachments/assets/4523e980-03aa-47e7-aee1-7285cce9fcad" />

- Refactored UploadFolderView as it was taking on too many responsibilities and made UploadFolderView only handle HTTP concerns, and created new FolderUploadService to orchestrate the logic
PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/144 Issue: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/134
- Implemented chronological ordering for non-git projects by extracting file timestamps from ZIP metadata. This feature enables projects to be displayed in chronological order (oldest first) based on their actual creation dates, not just git commit history
PR: https://github.com/COSC-499-W2025/capstone-project-team-8/pull/155 Issue: https://github.com/COSC-499-W2025/capstone-project-team-8/issues/147
- Tested that functionality remained the same and wrote new tests individual to each service
- Worked with Kyle McLeod on both features - he refactored the classifiers and analyzers so I branched off his work, and we worked simultaneously on our features interacting with each other and asking questions to see if what we were doing was right
- Reviewed multiple PRs
- Tested teammates code
- Tested my own and teammates code

What went well: 
- The refactoring helps our codebase become simpler and helps maintain a single responsibility principle
- Communicating with Kyle during this was good and trying to maintain a no merge conflict implementation
- Reviewing PRs and working with a teammate simultaneously was helpful in figuring out my implementation and to get a second opinion
- Bonus week work came in handy as it cleaned up our unnecessarily large files and components that had multiple functions which helped with implementation this week

What didn't go well:
- I had a hard time trying to understand our uploadFolderView as the component had over 700 lines of code and trying to figure out how to simplify the component without breaking functionality
- Some parts of refactor took longer because I ran into some logic errors once I moved the logic to somewhere else
- Trying to figure out how to retrieve a unix timestamp for a project that is non-git since there is no time for initial commit
- Our heuristics model markers weren't detecting some projects when testing, so I added those
- We potentially need to reconfigure to something more reliable other than heuristics since it is not accurate and marking most cases as 'coding projects'

Next week:
- I want to meet with the team and delegate our tasks and bring up potential reconfiguring of our heuristics model and see if there are better alternatives to implement
- I want to potentially start Issue https://github.com/COSC-499-W2025/capstone-project-team-8/issues/111 since Kyle implemented the projects models for our DB

Reflection: I learned the importance of a single responsibility principle and how it makes implementing new features a lot easier and makes components easy to understand. I also learned the importance of slowing down on implementation and reviewing what you currently have and the importance of refactoring before continuing. I learned more about the importance of proper refactoring and slowing down on new features in a project. I also learned that the way our JSON output works could use a tune-up/improvement since it is missing markers for certain project, and seems to flag most things as 'coding'. I also learned that work can be done quicker and more efficiently if you work with someone near you for feedback/review on the spot while implementing

Nov 24 - 30

![alt text](data/image-3.png)

- Implemented project ranking by contributor impact, wiring the new scoring logic into `/api/projects/ranked/` and updating database matching heuristics (Issue [#108](https://github.com/COSC-499-W2025/capstone-project-team-8/issues/108), PR [#186](https://github.com/COSC-499-W2025/capstone-project-team-8/pull/186))
- Added focused unit tests for signup GitHub email handling and contributor matching; exercised the endpoint in Postman to verify ranked output matches expectations
- Reviewed teammates’ PRs that expand project endpoint tests and the Azure LLM client, following their instructions and confirming test runs
- Tested their PRs 
- Reviewed PRs https://github.com/COSC-499-W2025/capstone-project-team-8/pull/179 & https://github.com/COSC-499-W2025/capstone-project-team-8/pull/178 & https://github.com/COSC-499-W2025/capstone-project-team-8/pull/191


What went well:
- Following a strict TDD cycle kept the new ranking logic reliable, and Postman verification matched unit-test expectations
- Collaborating with teammates on the LLM and project-endpoint PRs surfaced missing environment setup early, so we could unblock each other quickly

What didn’t go well:
- Docker test runs initially failed because the container lacked the Azure env vars; needed extra iterations to document the proper setup
- Mapping contributor emails revealed duplicate user data, so additional data cleanup was required before scores displayed correctly
- Trying to find a way to store projects created_at date from the JSON output of the file uploaded instead of saving it as the created_at of the date the project was uploaded

Next week:
- Present our milestone 1

- Begin milestone 2 related things


Reflection:
- We have made a lot of progress and utilized lots of different tools at our disposal, happy with the teams communications and work contributions so far
- Reviewing complex PRs highlighted the value of reproducible test instructions—especially when external services (Azure, Docker) are involved






