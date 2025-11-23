# Harper Kerstens's Weekly Logs
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
