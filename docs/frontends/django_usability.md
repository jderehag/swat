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

#Django usability


[TOC]


## Exploratory visualization
Currently the overall goal of the frontend is to enable "exploratory visualization" of metrics.
The reason for that is that no single clear-cut metric exists today to determine if code is good or bad.
Take for example mccabes cyclomatic complexity. Many people thinks its equivalent to subjective complexity but this is
simply not true. Some files will have huge mccabe number eventhough they are perceptibly simple.
For example, a function with an extremely repetetive switch case statement (say the naive case of translating enums to
strings). Such a function will have a huge mccabe number, eventhough its very easy to understand what it does (and is
very unlikely to have any faults in it).


This problem of not having any clear-cut metric is what inspired the exploratory visualization frontend. Where one
instead could allow the user to browse their own codebase and make their own conclusions instead.  
In essence letting them explore and play around with metrics as best they can.


###Purpose
1. One should be able to compare whatever metric across subsystem/file/function
2. One should be able to see how a subsystem/file/function has evolved over time
3. One should always be able to "zoom" on whatever view your have. What we mean with zoom is that from a subsystem you
   should be able to easily transition into looking at files, and from files you should easily be able to transition
   into functions.

To fulfill the above requirements we have created 2 views.

1. [Treemap](#Treemap)  
   The Treemap is meant to present the latest snapshot of the repo. It has the primary purpose of comparing metrics 
   across subsystems/file/functions.  
   For continous data (like nloc), it will take the latest value available in the database.  
   For discontinous data (like changerate or defects), it will sum the results from the last 6 months.  
2. [Charts](#Charts)  
   Is meant to represent a historical view for subsystem/file/function. The purpose would be to see how the component
   has evolved over time, but also with the possibility of comparing whatever component with another component.  


###Treemap
The Treemap is meant to present the latest snapshot of the repo. It has the primary purpose of comparing metrics across 
subsystems/file/functions  
For continous data (like nloc), it will take the latest value  
For discontinous data (like changerate or defects), it will sum the results from the last 6 months.

You can sort on 2 dimensions, either size or color where the 2 dropdowns will indicate which metric will correspond
to which dimension.

There is also a context menu if you right-click on a component where you can for instance get the physical filepath
to the component.

####Caveats
1. Will only render boxes if *both* metrics exist in the component (i.e both nloc AND defect_modifications must exist)
2. Effective complexity is only available on subsystem and file level.

###Charts
The idea is to very freely be able to select one or more components (subsystem/file/function).  
Then select the metrics to be applied.
Any metric is can be applied as either a line or a histogram.

The chart itself has 2 y-axes. Typically defect_modifications will be plotted on the right axis while any other metric
will be plotted on the left one.


* Line  
  Typically used for continous metrics (like nloc, complexity, number\_of\_tokens,..)


* Histogram  
  Typically used for discontinous metrics (added, changed, deleted, changerate, defects). There is also a slider
  where you can choose the bin size (binsize=3, means that we will divide each year with 3, and then sum all values
  within a bin to represent that specific bar).


* Export to CSV  
  You can export any data to CSV by plotting whatever you are interested in and then click the "export to CSV" button.

##[Description of metrics](/docs/metrics.md)
For a description of the various metrics have a look at [metrics](/docs/metrics.md)


##Browser recommendations
1. Chrome 5+
2. Firefox 5+
3. Internet Explorer 9+

However, it is still recommended to use the most recent Firefox or Chrome versions.


##Bug reporting & feature requests
[Contacts](/docs/README.md#contacts)  
[redmine](/docs/README.md#www-frontend)  

