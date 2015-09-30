[//]: <> (Copyright 2015, Jesper Derehag <jesper.derehag@ericsson.com> for Ericsson AB)
[//]: <> (All rights reserved.)

[//]: <> (Redistribution and use in source and binary forms, with or without modification,)
[//]: <> (are permitted provided that the following conditions are met:)

[//]: <> (1. Redistributions of source code must retain the above copyright notice, this list of conditions)
[//]: <> (and the following disclaimer.)

[//]: <> (2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the)
[//]: <> (following disclaimer in the documentation and/or other materials provided with the distribution.)

[//]: <> (THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED)
[//]: <> (WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A)
[//]: <> (PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY)
[//]: <> (DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO,)
[//]: <> (PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER)
[//]: <> (CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT, INCLUDING NEGLIGENCE)
[//]: <> (OR OTHERWISE, ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF)
[//]: <> (SUCH DAMAGE.)

[TOC]

#Metrics

## Line counts  
### nloc  
database column name: **change_metrics.nloc**  
metric_name: **nloc**

Number-of-lines-of-code.  
This is calculated as the number of new-line characters per file (and function).


### Diff counts
All diff counts are calculated using python difflib.unified_diff which is based on an algorithm published by 
Ratcliff and Obershelp under the hyperbolic name [gestalt pattern matching][unified_diff]

* added  
  database: **change\_metrics.added**  
  metric_name: **added**  
  The number of lines (nloc) that have been added since previous version.


* changed  
  database: **change\_metrics.changed**  
  metric_name: **changed**  
  The number of lines (nloc) that have been changed (not added or deleted) since previous version.  


* deleted  
  database: **change\_metrics.deleted**  
  metric_name: **deleted**  
  The number of lines (nloc) that have been deleted from the previous version.  


* changerate  
  database: **N/A**  
  metric_name: **changerate**  
  The sum of added, changed, deleted since previous version.  

##Number of tokens
database: **change_metrics.token\_count**  
metric_name: **token\_count**

The number of whitespace delimited words in each file-function


##Number of parameters
database: **change_metrics.paramater\_count**  
metric_name: **parameter\_count**

The number of parameters a function takes. If viewed on a subsystem or file level it indicates the sum of all functions
 up to the parent level.


##McCabes cyclomatic complexity.
database: **change_metrics.cyclomatic\_complexity**  
metric name: **cyclomatic\_complexity**  

###Theory
Measures the number of linearly independent paths through a program's source code.
It typically does this by building a graph where nodes are "commands" (i.e control statements in the language).

Furthermore, a number of studies have investigated cyclomatic complexity's correlation to the number of defects 
contained in a function or method. Some studies find a positive correlation between cyclomatic complexity and defects: 
functions and methods that have the highest complexity tend to also contain the most defects, however the correlation
between cyclomatic complexity and program size has been demonstrated many times and since program size is not a 
controllable feature of commercial software the usefulness of McCabes's number has been called to question.
The essence of this observation is that larger programs (more complex programs as defined by McCabe's metric) 
tend to have more defects.  
The above text is in parts taken from [Wikipedia/Cyclomatic_Complexity][wikipedia complexity]  
The article is really a recommended read for an overiew of Cyclomatic Complexity.

[McCabe original paper][mccabe original]

###Implementation
Calculated using [lizard][lizard]  
Lizard uses "fuzzy parsing" and is therefore rather poor at identifying method scopes.  
"fuzzy parsing" is fancy-speak for "finding control statements using regular expressions". 
So some methods (also macro/template functions) gets reported on the previous method (usually global scope).

##Effective cyclomatic complexity 
database: **N/A**  
metric name: **effective\_complexity**

###Theory
The effective cyclomatic complexity of a file.  
Calculated by the sum of all the functions with cyclomatic complexity >15 divided by the number of functions.  
Effective complexity as defined by [Vard Antinyan][Risky files]

###Implementation
FYI. since it's calculated on file level it doesn't exist on function level.  


##Defect modifications
database: **defect\_modifications**  
metric_name: **defect\_modifications**

The number of identified modifications for each defect per function. In other words, we save a row 
(with locality file/function) in the database for each identified commit that is marked as a defect-modification.

###Implementation
To classify a modification as a defect modification we parse the VCS for metadata matching a specific pattern.  


1. ClearCase  
   Search through any branch name matching regex, and report it as defect-modification branch if it has been
   delivered (anywhere)  

2. git  
   Search through each commit message looking for regex.

##Revisions
database column name: **change\_metrics**  
metric_name: **revisions**

1. ClearCase  
   Each new checkin on any of the LSV branches is counted as a revision.  
   LSV branches have either of the following branch names: *main, mpg\_lsv\_int, ggsn\_lsv\_int*

2. git  
   Each new commit is counted as a new revision.  
   In git we are only counting master branch.

##Defect density
database column name: **N/A**  
metric_name: **defect\_density**

Defect density is a metric that somewhat tries to indicate the average number of defects per lines of code.  
It is however highly controversial in that it makes a size estimation based on LOC, which poorly translates across
languages (and even inside languages but different coding paradigms). It is therefore a dangerous to use it as a
comparison between subsystems since without detailed knowledge about both systems one can't really know what programming
paradigms are used and if they are comparable. But that beeing said, it is still atleast an attempt at removing size 
as a confounding factor in estimating "quality". Variations on defect density definitions exist and you can read more 
about defect_density [here][defect density].  
In general, industry and academia prefers function points \(FP\) for size estimation. However calculating FP is so far
a manual process and are thus for practical reasons not implemented here. Instead we use:  

defect_density = defect\_modifications/nloc  

But once again, keep in mind that nloc is perceived as a poor size estimation metric, and results will be highly
contextual.


[unified_diff]:http://www.drdobbs.com/database/pattern-matching-the-gestalt-approach/184407970
[wikipedia complexity]:http://en.wikipedia.org/wiki/Cyclomatic_complexity
[lizard]:http://www.lizard.ws/
[mccabe original]:http://www.google.se/books?id=vtNWAAAAMAAJ&hl=sv&pg=PR1#v=onepage&q&f=false
[Risky files]:http://web.student.chalmers.se/~vard/files/Identifying%20Risky%20Areas%20of%20Software%20Code.pdf
[defect density]:http://softwaretestingfundamentals.com/defect-density/