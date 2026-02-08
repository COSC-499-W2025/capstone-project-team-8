# Harper Kerstens's Weekly Logs

- [September 15-21](#september-15-21)
- [September 22-28](#september-22-28)
- [September 29-October 5](#september-29-october-5)
- [October 6-12](#october-6-12)
- [October 13-19](#october-13-19)
- [October 20-26](#october-20-26)
- [October 27-November 2](#october-27-november-2)
- [November 3-9](#november-3-9)
- [November 16-22](#november-16-22)
- [November 23-29](#november-23-29)
- [November 30-December 6](#november-30-december-6)
- [January 5-11](#january-5-11)
- [January 12-18](#january-12-18)
- [January 19-25](#january-19-25)
- [January 26-February 7](#january-26-february-7)

## September 15-21

<img width="1090" height="643" alt="September15-21" src="https://github.com/user-attachments/assets/78cd1c97-3f9a-450c-a8d4-981e2753d42a" />


- Collaborated to create team requirements with team
- Discussed with other groups about their ideas for project
-  Revised project requirements based off feedback from other groups


## September 22-28

<img width="534" height="311" alt="Week4" src="https://github.com/user-attachments/assets/c1635b81-22b7-4214-9753-29a3c514af5a" />

- Discussed with other groups on their Architecture designs
- Researched Tech stack options for project
- Worked on Project Proposal Document

## September 29-October 5

<img width="1082" height="635" alt="September29-Oct5" src="https://github.com/user-attachments/assets/7f67060b-0d0d-4795-8edc-c0505b79d158" />

- Developed dataflow diagram with team members in class
- Met with peers to go over each others diagrams
- Reflected on our diagrams as a team
- Revised our diagrams based on feedback from peers

## October 6-12

<img width="1085" height="636" alt="October6-12" src="https://github.com/user-attachments/assets/d0b714b0-092f-4338-a827-f8721d3a1327" />

- Researched different python backend frameworks
- Discussed with team which backend framework to use
- Implemented Django backend framework
- Restructured Django set up based off team members feedback

## October 13-19

<img width="1085" height="629" alt="October13-19" src="https://github.com/user-attachments/assets/922de45f-2c9a-4352-a195-0747b4bc1f5a" />

- Implemented file upload functionality in Django backend
- Implemented basic categorization of uploaded files based off file type
- Testing new implemented features
- Refactored file upload code and backend to improve modular code structure
- Reviewed team members code and provided feedback

### What went well
 Made good progress on file upload helping to get the ball rolling on handling user uploads. Beginning to understand the Django framework and how to utilize it.

### What didn't go well
 Some confusion on how to best structure the backend for future features. Took more time than expected to implement file upload functionality due to unfamiliarty.
### What's next
Continue working on handling uploaded files and detecting repositories within uploaded files. Start segregating files based off found projects.


## October 20-26

<img width="1080" height="635" alt="October20-26" src="https://github.com/user-attachments/assets/8644fda1-efa4-4362-adb1-c27b276a52cf" />

- Continued work on file upload functionality
- Analyzer can now detect repositories in uploaded zip files
- Assigns tags to files based on file type and repository (repository root and assigned tag)
- Testing and debugging new features
- Reviewed team members code and provided feedback

### What went well
 Detecting repositories in uploaded files is a big step forward for the project. The analyzer is starting to take shape and we can begin thinking about analysis features. 
### What didn't go well
 Some issues with accurately detecting repository structures within uploaded files. Further refinement is needed to improve detection accuracy.
### What's next
 Continue working on refining repository detection and improving file tagging. Begin implementing analysis features based on detected repositories.

## October 27-November 2

<img width="1078" height="627" alt="October27-Nov2" src="https://github.com/user-attachments/assets/49d4a664-01cc-48e9-9558-a7335e73462a" />

- Fixed broken file analyzer functionality due to recent backend changes
- Refactored file analyzer to avoid excessively large files
- Reviewed others code and provided feedback
- Assited team members in their development

### What went well
 Was able to take some time to refactor the file analyzer when looking into issues. Improved modularity of code which should help with future development.
### What didn't go well
 This issues was unexpected which caused some delays in progress that was expected for this week. Timeline will have to be shifted slightly to accomodate for this.
### What's next
 Begin working on understanding files content. Reading text files and extracting useful information to better understand projects. Implement user consent features as well.

 ## Novermber 3-9
 
<img width="1078" height="632" alt="November3-9" src="https://github.com/user-attachments/assets/0f5c1d46-7d4e-4e2c-bac8-f81140c0f1c3" />

- Impemented user consent features for file analysis
- Enhanced file analyzer to read and extract text content from files
- Modularized file analyzer's extension checking to reduce file size.
- Reviewed team members code and provided feedback

### Completed PRs
| Pull Request | Issues addressed |
|---|---|
| https://github.com/COSC-499-W2025/capstone-project-team-8/pull/123  |  https://github.com/COSC-499-W2025/capstone-project-team-8/issues/105 |
| https://github.com/COSC-499-W2025/capstone-project-team-8/pull/122  | https://github.com/COSC-499-W2025/capstone-project-team-8/issues/113, https://github.com/COSC-499-W2025/capstone-project-team-8/issues/114  |

### What went well
Was able to successfully implement all tasks planned for this week. Stregthened the file analyzers content reading capabilities  which will be a big step towrads building a useful project analyzer. User consent features were also implemented to ensure the user has control over their data. 

### What didn't go well
Some unexpected challanges were implementing what happens the when the user doesn't give consent to have their files analyzed. I couldn't determine on if it made more sense to just return an error to the user or take in their input but not analyze it. After discussing with the team we decided to recieve their input but not analyze it to keep the system in an active useable state instead of returning the user with a road block.

### What's next
The plan for me for the next wee is to begin with a non AI understanding of analyzed files. I want to be able to return a useful analysis of the files to help make a more efficient AI analysis in the future. This will also be helpful for if the user does not want their data sent to an LLM.
### Reflection:
This weeks development went surprisingly well. After last week where I spent the majority of my time fixing issues I was prepared to have more delays in my development this week. However I didn't run into any major issues and was able to complete all my tasks for the week. I'm happy with the progress I made and I'm looking forward to continuing development next week.

 ## Novermber 16-22
 
 <img width="1071" height="634" alt="November16-22" src="https://github.com/user-attachments/assets/f0cc3694-320a-46d6-af0d-a36992cd1267" />
 
- Increased file analyzer's performance by reducing redundant scans for dependencies and modules
- Implemented file size limits so sub 5 line files are skipped during analysis
- Implemented skill extraction from analyzed files that produces a percentage breakdown based on frequeny of skils found in files
- Reviewed Team members code and provided feedback
- Received help from team members in understanding new project updates

### Completed PRs
| Pull Request | Issues addressed |
|---|---|
|  https://github.com/COSC-499-W2025/capstone-project-team-8/pull/160 | https://github.com/COSC-499-W2025/capstone-project-team-8/issues/137 |
| https://github.com/COSC-499-W2025/capstone-project-team-8/pull/161 | https://github.com/COSC-499-W2025/capstone-project-team-8/issues/107 |

### What went well
    This week I was able to make significant improvements to the file analyzer's performance. This process was fairly painless and I was able to implement the changes quickly. It did take me a minute to mentally map out how I wanted to implement the skill analyzer feature but once I had a plan it was smooth sailing from there.

### What didn't go well
    Testing my teamates code changes took longer than expected this week. As the database is becoming more central to the work we are doing it takes more time to figure out if things are working and data is correctly being stored. This is something that I will get more proficient at as we continue, however, this week it was more challenging than I expected.


### What's next
    The next steps would be to connect the skill analyzer to the database so that the results can be stored. I didn't have enough time this week to implement that connection but it is a high priority for next week. I'd like to have projects be able to be recognized when a duplicate upload occurs and that way the skill break down can be based off the all time uploads for a user.

### Reflection:
    This week went well overall. I was a little worried about the progress I would be able to make due to requirements from other classes. However, things went smoothly during the time I spent on the project which alieviated some of my stress. Development went well which is always a good feeling. I'm looking forward to next week as we get closer to Milestone 1s due date. We are making good progress as a team and things are shaping up nicely.


 ## Novermber 23-29
 
 <img width="1077" height="634" alt="November23-29" src="https://github.com/user-attachments/assets/5569fdc7-e1cb-4b0a-b8c8-2ab58e833633" />

- Created routes for project datamanagement (get all projects, get project by ID, delete project)
- Fixed database date storage issue to allow for chronological ordering of projects
- Began implementation of chronological skill analysis based off project upload dates
- received help from team members in fixing the databse date issue


### Completed PRs
| Pull Request | Issues addressed |
|---|---|
| https://github.com/COSC-499-W2025/capstone-project-team-8/pull/178 | https://github.com/COSC-499-W2025/capstone-project-team-8/issues/170 |
| https://github.com/COSC-499-W2025/capstone-project-team-8/pull/191 | https://github.com/COSC-499-W2025/capstone-project-team-8/issues/190 |

### What went well
    This week one thing that went well was my implementation of routes regarding the projects stored in database. I was able to get all the routes I wanted such as getting all projects, getting a project by its ID, and deleting a project. All of these were faily painless to implement once I figure out how to get things going.

### What didn't go well
    One thing that didn't go well this week was implementing the chronological skill analysis. I had a plan on how to do it but once I started I realized there was an error with how project dates were being stored in the database. This logic I was going to require on for my new implmentations. I ended up spending lots of time fixing the date issue and then I ran out of time to implement the chronological skill analysis this week pushing it to next week.



### What's next
    Whats next is building off of what I fixed this week to implement the chronological skill analysis. Once that is done most major features for milestone 1 will be completed and I will begin working on polishing features and fixing bugs that arise.


### Reflection:
    Overalll I am happy with my progress this week. Although I didn't get everything done that I wanted to, fixing the database issue was very high priority once we discoverd it. Fixing this will allow for easier development in the future and there should be no more issues that arise in this regard. I'm excited to build chronological skill ordering next week as it's development should be relatively painless following this week.

 ## Novermber 30-December 6
 
 <img width="1067" height="628" alt="November30-Dec6" src="https://github.com/user-attachments/assets/7e3075dd-5c59-43ca-a4d5-477e76445967" />

- Created Team contract for project
- Presented project progress to class
- Implemented chronological skill analysis based off project upload dates
- Tested and debugged new feature
- Reviewed team members code and provided feedback


### Completed PRs
| Pull Request | Issues addressed |
|---|---|
| https://github.com/COSC-499-W2025/capstone-project-team-8/issues/173 | https://github.com/COSC-499-W2025/capstone-project-team-8/pull/199   |


### What went well
    This week the chronological skill analysis was the highlight for what went well. I was able to successfully implement the feature and it works as intended. It was sastisfying to see it come together especially after being delayed in the previous week with its implementation.

### What didn't go well
    Nothing in particular went poorly this week. I was able to complete all my tasks without any major issues. There were some minor bugs that came up during testing of the new feature but they were quickly resolved.


### What's next
    The next steps will be to begin looking towards milestone 2 as we polished off near everything we wanted to for this milestone. I will begin looking into what features we want to implement next and start planning for their development.

### Reflection:
    This week went well overall. I was able to complete everything I set out to do without any major issues. The chronological skill analysis was a big win for me personally as it was a feature I was excited to implement. I'm looking forward to moving onto milestone 2 and continuing development on the project.

## January 5-11
 
<img width="1080" height="635" alt="January5th-11th" src="https://github.com/user-attachments/assets/1de75df8-8ec4-4b4c-b3b9-1ebab57fd7bd" />


- Linked Frontend to Backend for project upload and analysis
- Implemented contribution analysis feature to show user a more detailed breakdown of their contributions
- Added ability for user to upload photo for their project profile
- Tested and debugged new features
- Reviewed team members code and provided feedback


### Completed PRs
| Pull Request | Issues addressed |
|---|---|
|https://github.com/COSC-499-W2025/capstone-project-team-8/pull/214  | https://github.com/COSC-499-W2025/capstone-project-team-8/issues/212 https://github.com/COSC-499-W2025/capstone-project-team-8/issues/213   |
|https://github.com/COSC-499-W2025/capstone-project-team-8/pull/211 | https://github.com/COSC-499-W2025/capstone-project-team-8/issues/210 |


### What went well
This week the linking between the frontend and backend went well. I was able to successfully connect the two and have them communicate properly. I didn't spend much time customizing the front end however and would like to make some group decisions on the design in the future.

### What didn't go well
 It took me quite a while to figure out how to add the contribution metrics. I wasn't sure what information I could obtain from the .git and how to break it all down in a useful manner. After some research I was able to figure out what was possible and implement it but it took longer than I expected.


### What's next
Going forward I would like to continue working on tasks relating to Milestone 2. I would also like to begin thinking about the design of the overall product as we move closer to a useable application. This would prevent any unneccesary redesigns in the future.

### Reflection:
This was a week that didn't have as much progress overall compared to previous weeks. However, I still feel great about our project and progress as a group. We are steadily moving towards our goals and getting a usable resume from what we have analysed was very exciting to see this week.
 
## January 12-18
 

<img width="1086" height="638" alt="January12-18th" src="https://github.com/user-attachments/assets/078fb130-1a24-4e3d-90a6-684b5cf24cc8" />

- Implemented login/signup ability
- Users can pull previous projects from database
- Users can upload profile picture alongisde change any account information
- Users can upload a photo per project that now saves to the database
- Implemented dashboard on main page


### Completed PRs
| Pull Request | Issues addressed |
|---|---|
|  https://github.com/COSC-499-W2025/capstone-project-team-8/pull/236 |  https://github.com/COSC-499-W2025/capstone-project-team-8/issues/235 |
|  https://github.com/COSC-499-W2025/capstone-project-team-8/pull/237 |   |
| https://github.com/COSC-499-W2025/capstone-project-team-8/pull/238  | https://github.com/COSC-499-W2025/capstone-project-team-8/issues/213   |

### What went well
This week develpment was very smooth across the board. There were no hitchups or unexpecting issues that arrised causing delays in progress. I was able to get everything done I had planned out for this week.

### What didn't go well
I found myself spending time on unenessacary features this week and had to stop myself a few times from wasting time. I was getting down rabbit holes for cool little interativity features but decided to shelve them for now as it's very low priority work.


### What's next
Next week would be continuing what we built off of and focusing on putting together a resume builder. Now that we have a resume generator we need to give the users the option to pick and designing/building an interface to put it together is key to the work we have done so far.

### Reflection:
I'm very please with both my work and the groups work this week as lots was done. We are feeling good ahead of the peer testing in a few weeks and our product is continuing to go. There were minimal conflicts this week which was also nice, stress free weeks are very much appreciated.

## January 19-25
 
<img width="1079" height="634" alt="January19-25th" src="https://github.com/user-attachments/assets/e88f1160-6f8b-49a2-899c-740724022445" />



- Implemented resume builder interface
- Connected backend features to resume builder frontend
- Users can now select from analyzed projects to include in their resume
- Users can customize the layout and design of their resume
- Users can download their resume
- Reviewed team members code and provided feedback


### Completed PRs
| Pull Request | Issues addressed |
|---|---|
| https://github.com/COSC-499-W2025/capstone-project-team-8/pull/264  | https://github.com/COSC-499-W2025/capstone-project-team-8/issues/231  |

### What went well
This week development was smooth and there was no major hitchups outside of one. I was able to get the interface done and looking nice. Connecting the backend features to the frontend was also nice as we were able to see the features start to come together more.
### What didn't go well
This week I spent a lot of time trying to fix a bug in my newly implemented feature. For some reason when typing in one of the text fields the text would be entered backwards. After spending a good amount of time trying to debug it I finally figured out the issue and was able to fix things.


### What's next
The system still has some refining to do and theres more work to be done before the resume builder interface is finished. Next week I plan to continue working on developing the resume builder and fixing any bugs that arise along the way.

### Reflection:
Overall I'm happy with the progress made individually this week. As classes ramp up again I know it will be harder to spend extra time on the project so I'm glad I was able to lay a strong foundation for the resume builder. Future development should be smoother now that the base is there.


## January 26-February 7

 <img width="1103" height="643" alt="January26-Febuary7th" src="https://github.com/user-attachments/assets/a932c5b3-e812-4654-bb15-1323c8370d10" />

- Implemented additional features for resume builder
- Users can now chose from multiple templates for their resume
- Users name and education now automatically populate on the resume based off their account information
- Reviewed team members code and provided feedback


### Completed PRs
| Pull Request | Issues addressed |
|---|---|
|https://github.com/COSC-499-W2025/capstone-project-team-8/pull/275   | https://github.com/COSC-499-W2025/capstone-project-team-8/issues/272 https://github.com/COSC-499-W2025/capstone-project-team-8/issues/273|

### What went well
This week development went well and I was able to implement everything I had planned to do. Nothing got too complicated and I didn't run into any overberaing issues. The resume builder is starting to come along more which is nice to see

### What didn't go well
We wanted to go back and work on some things based off the feaedback from heuritic evaluation. Development for these adjustments went well but it just ended up taking up some unplanned time this week.



### What's next
Next would be to continue expanding upon features for the user. Consistent flow and styling, more interatctivity and a more in the loop feedback system to help ease the understanding and the state of the system.

### Reflection:
Overall I am very happy with the progress made and the project itself. Things continue to come together and we are making good progress. Looks of exciting features are being implemented and things are increasingly becoming more developed.
