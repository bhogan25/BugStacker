# BugStacker
BugStacker is a project management software system that allows managers and developers to identify software defects and issues by creating tickets. In addition, BugStacker is my final project submission for HarvardX's CS50W Programming with Python and JavaScript.

# Resource Hierarchy
From top to bottom:
1. Project
2. Workflow
3. Ticket

# Resource Identification Syntax
Each resource (Projects, Workflows and Tickets) should be uniquely identifiable for ease of machine searching as well as human readability. The unique identifiers for these resources are referered to as the Resource Codes. The following resource codes and their characteristics are listed below.

## Machine Readable
| Resource | Django Model Field | Value Range | Initial Value | Uniqueness with respect to |
| --- | --- | ---| --- | ---|
| Project | PositiveSmallIntegerField |  0 - 32767 | 1 | Application |
| Workflow | PositiveSmallIntegerField |  0 - 32767 | 0 | Parent Project |
| Ticket | PositiveSmallIntegerField |  0 - 32767 | 1 | Parent Workflow |

## Human Readable
| Resource | Type | Possible Instances | Initial Value | Uniqueness |
| --- | --- | ---| --- | --- |
| Project | String | 32767 | P1| Application |
| Workflow | String | 1.0737e9 | P1-W0 | Application |
| Ticket | String | 3.5182e13 | P1-W0-T1* | Application |
