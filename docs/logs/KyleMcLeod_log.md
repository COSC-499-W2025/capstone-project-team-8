# Kyle McLeod's Weekly Logs
## September 15-21
<img width="624" height="358" alt="Screenshot 2025-09-21 144528" src="https://github.com/user-attachments/assets/abef3302-eb64-4093-b540-9c8f9dc87dd8" />

- Created list of functional and non-functional requirements with team
- Revised requirement list after feedback
- Discussed possible tech stack with team
- File structure organizationin GitHub repository

## September 22-28
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/a6999f11-c3db-4aa2-9b07-e669e74e2122" />

- Put together the project proposal template
- Worked on a system architecture diagram with the team
- Revised the diagram based on other teams suggestions
- Helped plan the stack we will use

## September 29 - October 5
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/239e9fcd-13e5-4555-b5e4-a13b394b003d" />

- Helped create level 0 and level 1 diagrams
- Got feedback from other groups and revised the diagrams accordingly
- Created and organized a Kanban board so we can keep track of the issues we create
- Researched on other companies that provide a solution on the project task (this can be used to understand the system requirements more and allow us to areas where our project could offer a more effective or innovative approach)

## October 6-10
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/7fca0375-5f18-4cc4-b697-c69d39765a72" />

- Installed Next.js to a front end folder (we probably won't be using this until miletsone 2 but it is good to see the whole project folder setup)
- Documented on how to start the front end server
- Created issues on our Kanban board and assigned tasks to teammates
- Reviewed Harper and Charlie's pull requests
- Suggested revisions on the backend folder structure
- Read Django docs to learn how to create API routes

## October 13-17
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/023f0d28-72e4-4251-8409-b422113aea29" />

- created a document proposing a plan for our AI analysis layer
- compared multiple cloud hosting platforms for AI hosting
- the document has 3 different ooptions we can choose and we will further discuss the final choice in our next team meeting
- created issues on our kanban board
- reviewed harpers pull request
- reviewed matins pull request
- updated main readme file

## October 20-24
<img width="624" height="358" alt="image" src="https://github.com/user-attachments/assets/d7c0fedd-f40c-41e3-85f2-eca0af9093c7" />

- designed and created an AI layer that will play a crucial role in getting insights on files
- scalable and easily portable so we can host it on any cloud host
- chose a cloud host provider and am now going to work on deploying the model so we can use a powerful model for testing
- did weekly logs
- reviewed harpers pull request on file classification
- reviewed matins pull request on database configuration
- populated kanban board with more tasks for next week

## October 27-31
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
