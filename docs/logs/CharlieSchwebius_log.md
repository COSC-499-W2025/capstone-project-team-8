# Charlie Schwebius' weekly logs
[Week 3](#week-3-(september-15-21))


## Week 3 (September 15-21)
<img width="1923" height="1123" alt="Screenshot 2025-09-21 111401" src="https://github.com/user-attachments/assets/3816e1e3-ec1a-42a8-878a-b87766521230" />

- Worked as a team to create requirements document
- Reviewed requirements document with other teams to gather input and insight.
- 
## Week 4 (September 22-28)
<img width="1085" height="629" alt="image" src="https://github.com/user-attachments/assets/2203e8d0-580b-41bd-975a-595e45fcf2e2" />

- Collaborated with team to build a system architecture diagram
- Collaborated with team to make project proposal document
## Week 5 (September 29 - October 5)
<img width="1088" height="637" alt="Screenshot 2025-10-05 175922" src="https://github.com/user-attachments/assets/3379a430-5631-4831-ade4-7996fb767e0a" />

- As a team, created Level 0 and Level 1 Data Flow Diagrams
- Met with other teams to review each other's diagrams
- Reflected together as a team on our diagrams (What did we like? What did we overlook? etc.)

## Week 6 (October 6 - 12)
<img width="1897" height="1103" alt="image" src="https://github.com/user-attachments/assets/871fe97d-2836-4795-be3c-7824b644ba5b" />

- Revised Data flow and system architecture diagrams to match what we've discussed as a team
- Created work breakdown structure following the lecture example
- Added descriptions to data flow and system architecture diagrams to explain our thought process and how to read them
- Spent time learning about Django
- Spent time refreshing my mind on Docker

## Week 7 (October 13 - 19)
<img width="1906" height="1114" alt="image" src="https://github.com/user-attachments/assets/f9f7f7a0-d0d3-4734-832b-bb22f036c165" />

- Continued research into our selected framework (Django)
- Researched solutions to some of our core problems (File input, data scraping, finding file contributors, attributing contributions, external AI analysis tools)

#### WHAT WENT WELL: 
- Gathered lots of helpful information to benefit our project
#### WHAT DIDN'T:
- Failed to produce a PR


## Week 8 (October 20 - 26)
<img width="1910" height="1117" alt="image" src="https://github.com/user-attachments/assets/f1170f39-a6af-4abe-856a-c7b504bce476" />

#### PR : #74

- Created heuristic project classifier based on file names, file types, and folder names
- Created tests and documentation for this classifier
- Researched Ollama and other local LLM models (How good are they for what we need, etc.)
- Troubleshot local machine issues (issues connecting to mySQL in Docker, issues with Next.js packages)

#### WHAT WENT WELL: 
- Successfully created a heuristic classifier to categorize projects.
- Sorted out local machine setup

#### WHAT DIDN'T
- Wasted a LOT of time troubleshooting machine issues, leading to my PR going up later than I hoped
  
## Week 9 (October 27 - Nov 2)
<img width="1880" height="1094" alt="image" src="https://github.com/user-attachments/assets/88a7d061-f04c-4693-9055-397b1ee2ec3c" />

#### PR : #96

- Recfactored JSON output from file uploads to be more readable and usable for processing
- Refactored small protion of analyzers.py to be more adaptable to coming features (Non-git project detection)
- Refactored tests to accomodate JSON changes
- Updated documentation 
- Planned some backend pre-AI analysis (Coding Language and Framework Detection)

#### WHAT WENT WELL: 
- Successfully refactored JSON output and tests
- Got a clearer understanding of what we are doing in the coming weeks

#### WHAT DIDN'T
- Wasted EVEN MORE TIME troubleshooting machine issues
- Time management in general (difficult with a full course load)

NEXT WEEK: Implement Coding Language and Framework Detection


## Week 10 (Nov 3 - Nov 9)

<img width="1922" height="1124" alt="image" src="https://github.com/user-attachments/assets/3d09b849-9310-49d0-9d4b-82b3c2d2d5d1" />

#### What I did:

- Implemented code to detect langauges used in coding projects
- Implemented code to detect frameworks used in coding projects
- Tested functionality of both of these
- Reviewed and tested teammates PR's 

#### My PR's: 

#121: Coding language and framework detection enhancement

#### WHAT WENT WELL: 
- Successfully implemented both of these with minimal issues
- Completed my work and PR a lot earlier than past weeks

#### WHAT DIDN'T
- Everything went pretty smoothly

  #### REFLECTION
Overall, I think our team made pretty good progress. With us now having framework detection and with our LLM service gaining file-upload capabilities, we are getting very close to a finished product. Right now we have a lot of momentum, and I think with my knowledge of the current preprocessing, I can do a very good job of implementing the non-AI analysis functionality.

NEXT WEEK: Non-AI Analysis functionality (Resume Items++)


## Week 12 (Nov 17 - Nov 23)

<img width="1879" height="1089" alt="image" src="https://github.com/user-attachments/assets/bb74b283-fb9b-4628-8539-bd8b1bf4e773" />

#### What I did:

- Implemented resume skills extraction module to automatically detect professional skills from projects
- Created tests to ensure functionality
- Updated documentation in ./src/bacckend/README.md to reflect new JSON response
- Reviewed teammates code

#### My PR's: 

#162

#### WHAT WENT WELL: 
- Successfully implemented a resume skills extraction system
- All tests pass with no errors
- Skills are contextually inferred and resume-appropriate
- Fixed critical gap where creative projects weren't getting skills extracted
- Communicated with Harper Kerstens to ensure skill detetcion implementations serve unique purposes

#### WHAT DIDN'T
- Initial implementation had too many redundant/assumed skills that needed refinement
- Took several iterations to get the framework vs. skill separation right

#### REFLECTION
This week was very productive. The resume skills extraction feature is a major addition to our project's non-AI analysis capabilities. Some of my teammates had issues with the heuristic project classifier I developed previously, so I will definitely help them with their issues in the coming week.

NEXT WEEK: Generate actual resume bullet points based on new generated data + Help tune heuristic classifier

## Week 13 (Nov 24 - Nov 30)

<img width="1877" height="1097" alt="image" src="https://github.com/user-attachments/assets/fb651ad0-8f72-496c-92d9-762cf4a320ab" />

#### What I did:

- Implemented code to properly read PDF files
- Implemented code to analyze the content of text-based files
- Implemented code to enhance the non-AI resume skill generation feature, accounting for new text analysis
- Implemented code to generate a resume item (bullet points) without AI, based on new and old analysis features (skills, languages, frameworks, text analysis)
- Tested functionality of all 3 PRs
- Reviewed and tested teammates PRs 

#### My PR's: 

#188: implement PDF reading, Content analyzer for non-ai text document analysis 
#189: Content based resume skills
#194: Non ai resume item 

#### WHAT WENT WELL: 
- PDF reading functionality wasn't difficult to implement with the assistance of Python packages
- Resume skill feature is now more comprehensive, and actually generates results for text-based projects (novels, research papers, blogs, etc.)
- We now satisfy the alternative analysis requirement

#### WHAT DIDN'T
- Initially, I was only implementing a resume item feature, but gaping holes in our non-AI analysis became too big to ignore
- As a result, I had to restart after completing an initial implementation of the resume item generator.
- Implementation of these new features was incredibly time-consuming, preventing my work on the other 4 classes I am taking 

  #### REFLECTION
At this point, I think we are in a very good place for the end of milestone 1. Hiccups this week could have been avoided with better planning, so ultimately that's something to remember for milestones 2 and 3. I am happy with the current implementation of the non-AI analyses, but there are definitely refinements to be made as I've discovered through this week's development.

NEXT WEEK: Bug fixes and milestone wrap-up

## Week 14 (Dec 1 - Dec 7)

<img width="1886" height="1101" alt="image" src="https://github.com/user-attachments/assets/d4236df3-17b2-41ea-a274-83becb173f85" />

#### What I did:

- Fixed bug that ALWAYS created a fallback project, which would also save in the database
- Reviewed and tested teammates' PRs
- Proofread and reviewed Team Contract

#### My PR's: 

#208: Fix project 0 appearing unnecessarily

#### WHAT WENT WELL: 
- The bug fix was small and did not interrupt existing test functionality
- Caught some grammatical errors in the Team Contract

#### WHAT DIDN'T
- Poor time management led me to submit my pull request later than desired.

  #### REFLECTION
At this point, I think we are well set for milestone 1. Lots of bug fixes and refinements this week really help perfect our current implementation. Unfortunately, I have a recurring theme of late PRs, which is something I MUST change for milestone 2.

NEXT WEEK: Bug fixes and milestone wrap-up


## Milestone 2 Week 1 (Jan 5 - Jan 11)

<img width="1909" height="1110" alt="image" src="https://github.com/user-attachments/assets/4ae12b8d-3c2e-47dd-b752-cd8ef0694057" />

#### What I did:

- Started work on customizable portfolio functionality
- Helped troubleshoot an issue with Harper's PR
- Reviewed and tested teammates' PRs
  
#### My PR's (UNFINISHED -- TO BE COMPLETED NEXT WEEK): 

#220: Implement Portfolio Functionality

#### WHAT WENT WELL: 
- Was able to quickly troubleshoot Harper's PR, which allowed me to review it faster.
- Gave thoughtful reviews and effectively tested code

#### WHAT DIDN'T
- Poor time management led me to submit my pull request later than desired.
- Need to discuss with the team about the implementation of my PR, as it is integral to further project development

  #### REFLECTION
I made a fatal mistake by being late on my PR once again. It is a large PR, but I should have been better about my planning. Fortunately, I have made solid progress on it, but I absolutely need to coordinate with the team to ensure the best implementation. I am still optimistic about the rest of this Milestone, though; there seem to be fewer requirements.

NEXT WEEK: Discuss with the team and continue work on Portfolio implementation

## Milestone 2 Week 2 (Jan 12-18)

<img width="1878" height="1099" alt="image" src="https://github.com/user-attachments/assets/d2f50349-300f-48f9-9339-e51e0af4ecb1" />

