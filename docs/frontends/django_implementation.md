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
#Django implementation


[TOC]


##Directory description
    ___MetricsViewer(dir):  
    |   Contains Django project files and settings.  
    |   Contains very little code specific to our Django application.  
    |  
    |___vizualisation(dir):  
    |   "Our" Django app which contains the front end code.  
    |   |  
    |   |___static(dir):  
    |   |   Contains all .ts, .scss, compiled .css/.js and library files.  
    |   |  
    |   |___templates(dir):  
    |   |   Contains all .html template files.  
    |   |   A template is a special django feature see: 
    |   |   [django template language](https://docs.djangoproject.com/en/1.7/topics/templates/)  
    |   |  
    |   |___templatetags(dir):  
    |   |   Contains filter tamplates.  
    |   |   Filters is a way to inject transforming code into django templates.
    |   |  
    |   |___urls.py:  
    |   |   This file handles the URL:s for the web page.  
    |   |  
    |   |___views.py:  
    |       The main file of the django app.  
    |       Contains a controller method (a.k.a. a view) for each url or request. It is divided up in two parts,  
    |       one for the treeview and one for line view. It also some data handling methods used by the line chart.  
    |  
    |___manage.py:  
        Runs and manages the server.  

##External dependencies
Any python requirements needed can be read in [INSTALL](/docs/INSTALL.md) 

##JavaScript build dependencies
We use Node and Npm packages in our development environment. [Read more](/docs/frontends/django_development_guide.md)


###Web libraries:
Note that all web libraries are accessed through local, static files.

The links to the licensed are the ones that are linked on the libraries
individual websites. (Some pages link directly to the license page, and
other have described the license on their respective page).

1. *jQuery.*
    A general purpose library that is used for manipulating the DOM, event handling and server calls.
    http://www.jquery.com/
    License: MIT -> [https://github.com/jquery/jquery/blob/master/LICENSE.txt]()

    jQuery plugins:
        *fancytree*
            A library that allows you to view data in a hierarchical tree view.
            https://github.com/mar10/fancytree
            License: MIT -> [https://github.com/mar10/fancytree/blob/master/LICENSE.txt]()

2. *D3.js.*
    A JS+CSS charting library. Used for the line chart and tree map.
    Used by C3 and D3 plus.
    http://www.d3js.org/
    License: BSD -> [https://github.com/mbostock/d3/blob/master/LICENSE]()

3. *D3plus.js.*
    A JS+CSS charting library. Used for the tree map.
    This library uses D3 as base.
    http://www.d3plus.org
    License: MIT -> [https://github.com/alexandersimoes/d3plus/blob/master/LICENSE]()

4. *C3.js.*
    A JS+CSS charting library. Used for the line chart.
    This library uses D3 as base.
    http://www.c3js.org
    License: MIT -> [https://github.com/masayuki0812/c3/blob/master/LICENSE]()

5. *Twitter Bootstrap.*
    A JS+CSS look and feel framework used for different UI components. (Menus, icons etc.)
    http://www.getbootstrap.com/
    License: MIT -> [https://github.com/twbs/bootstrap/blob/master/LICENSE]()

6. *Mustache.js.*
    A simple template rendering library which in our case is used for frontend rendering.
    https://github.com/janl/mustache.js/
    License: MIT -> [https://github.com/janl/mustache.js/blob/master/LICENSE]()

7. *DefinitelyTyped.*
    A collection of type definitions for the Javascript libraries we use. Used for type safety and
    simplifies Javascript-Typescript interop.
    https://github.com/borisyankov/DefinitelyTyped
    License: MIT -> [https://github.com/borisyankov/DefinitelyTyped/blob/master/LICENSE]()


## RESTful API
###api/v0/:  
####Resources
1. /totals  
   N/A

   1.1 /totals/change\_metrics  
       **fields:** date, added, changed, deleted, nloc, parameter\_count, token\_count, cyclomatic\_complexity

   1.2. /totals/defects  
     **fields:** date, defect\_id  
     if bins attribute is supplied, defect\_id is replaced by number of distinct defects

2. /subsystems  
   **fields:** subsystem\_id, subsystem

   2.1 /subsystems/change\_metrics  
       **fields:** subsystem\_id, date, added, changed, deleted, nloc, parameter\_count, token\_count, cyclomatic\_complexity

   2.2. /subsystems/defects  
        **fields:** subsystem\_id, date, defect\_id  
        if bins attribute is supplied, defect\_id is replaced by number of defects

   2.3. /subsystems/{subsystem_id}/change\_metrics  
        **fields:** date, added, changed, deleted, nloc, parameter\_count, token\_count, cyclomatic\_complexity

   2.4. /subsystems/{subsystem_id}/defects  
        **fields:** date, defect\_id  
        if bins attribute is supplied, defect\_id is replaced by number of defects


3. /files  
   **fields:** subsystem\_id, file\_id, file

   3.1 /files/change\_metrics  
       **fields:** file\_id, date, added, changed, deleted, nloc, parameter\_count, token\_count, cyclomatic\_complexity

   3.2. /files/defects  
        **fields:** file\_id, date, defect\_id  
        if bins attribute is supplied, defect\_id is replaced by number of defects

   3.3. /files/{file_id}/change\_metrics  
        **fields:** date, added, changed, deleted, nloc, parameter\_count, token\_count, cyclomatic\_complexity

   3.4. /files/{file_id}/defects  
        **fields:** date, defect\_id
        if bins attribute is supplied, defect\_id is replaced by number of defects

4. /functions  
   **fields:** file\_id, function\_id, function

   4.1 /functions/change\_metrics  
       **fields:** file\_id, function\_id, date, added, changed, deleted, nloc, parameter\_count, token\_count, cyclomatic\_complexity

   4.2. /functions/defects  
        **fields:** file\_id, function\_id, date, defect\_id
        if bins attribute is supplied, defect\_id is replaced by number of defects

   4.3. /functions/{function_id}/change\_metrics  
        **fields:** date, added, changed, deleted, nloc, parameter\_count, token\_count, cyclomatic\_complexity

   4.4. /function/{function_id}/defects  
        **fields:** date, defect\_id
        if bins attribute is supplied, defect\_id is replaced by number of defects

####Filters/transform
Each resource can selectively be rendered as either json or csv by apppending formating to the resource name.

All resources can be filtered and/or transformed with the following parameters:

1. from=iso8601  
   Filter values 'from' datetime, default=epoch

2. to=iso8601  
   Filter values 'to' datetime,  default=datetime.now()

3. fields=(comma separated list with fields to include)  
   valid fields depends on the resource.

4. bins=integer  
   Transforms those fields where it makes sense (added, changed, deleted, defects, ...) into a histogram. 
   I.e, it will divide yearly results with bins, meaning bins=2 will divide each year in 2, and then sum values
   where it makes sense (added, changed, #trs) within each bin. 
   For those values where it does NOT make sense to transform(nloc, cyclomatic_complexity,...), it will select 
   value from the last date in the bin. If you want to sum all values within daterange, use bins=0.


####Exmples

http://example.com/api/v0/subsystems.json
Returns a json array with subsystem_id, subsystem

http://example.com/api/v0/subsystems/41/change_rate.json?from=2014-01-01
Returns a json array with all fields for subsystem\_id=41 ranging from 2014-01-01 to now.

http://example.com/api/v0/files/5/change_rate.json?from=2014-01-01?to=2015-01-01T16:00:00?bins=12?fields=added,nloc
Returns a json array for file\_id=5. Since values are filtered between 2014-01-01 -> 2015-01-01T16:00:00 (i.e 
range is 12 months, and since bins=12, it means we will create 1 bin for each month).
Array will contain 12 rows (one for each month), date will be last date according to bin and added will have been
summed within each bin. nloc will be from last value in bin (same as date).


## Additional resources
[https://docs.djangoproject.com/en/dev/ref/django-admin/#django-admin-runserver]()

--------------------------------------------------------------------------------
