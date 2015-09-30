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

#The frontend build tools and process
We use Node.js and it's package manager, npm, to perform various build steps in the frontend environment. Notably we use
Typescript to compile to Javascript and Sass to compile to CSS. Both of these are supersets of the Javascript/CSS which add
additional features.

In order to develop the frontend you need to:

1. Install node
2. Install npm. Recent node versions include npm. Check if node installs npm by default before trying to install npm.
3. Install our npm package dependencies
4. Run gulp which takes care of everything for you :-)


##Installation
###Installing node
Node can be found in the Ubuntu repositories. I do NOT reccomend installing this
version as it's usually very outdated. I reccomend using NVM, the node version manager to easily install and manage
versions of node. If this option is not available or you do not have sudo access, you could build node from source.

[Link to NVM](https://github.com/creationix/nvm)

[Building node from source (without needing sudo permissions)](https://gist.github.com/isaacs/579814)

###Installing npm
Recent node versions include npm by default, but if your version does not see
[https://docs.npmjs.com/getting-started/installing-node]()

###Installing the npm packages:
1. Enter the static directory. Here a *package.json* file should be located. This lists all of the node dependencies and allows
you to easily install them.
2. Install the npm dependencies using *npm install*. All of the required packages should be installed in a new directory *node_modules*.
Now you can start building using gulp by calling *./node_modules/gulp/bin/gulp.js* in the static directory.

        cd $ROOT/www/MetricsViewer/visualization/static/visualization/
        npm install
        ./node_modules/gulp/bin/gulp.js

In case you decide to add new npm packages and gulp plugins make sure to **UPDATE** *package.json*. Usually this is done when installing the
new package and adds the dependency to package.json.

        npm install --save <package-name>

Saves the dependency as a production (or deployment) dependency. Meaning that these packages are required to run the project.

        npm install --save-dev <package-name>

Saves the dependency as a development dependency. Meaning that in order to develop the project you need to install
that package. **Usually** this is what you need as all of our deployment dependencies and libraries are downloaded as standalone files
and saved in

        $ROOT/www/MetricsViewer/visualization/static/visualization/lib


##The frontend development tools

###Gulp
Gulp is a task runner for Javascript, similar to Make for C or Maven for Java. We use it to compile Typescript to Javascript
and Sass to Css. Gulp watches files and automatically compiles them on change. If Livereload is installed in your browser it reloads
your site when any changes occur during development.

If you have followed the npm installation instructions above, a local gulp installation can be executed by calling

        ./$ROOT/www/MetricsViewer/visualization/static/visualization/node_modules/gul/bin/gulp.js

The following gulp commands are available

        gulp		    - compiles everything once
        gulp treemap    - compiles the Typescript files for the lineview site once
        gulp lineview   - compiles the Typescript files for the treemap site once
        gulp sass 	    - compiles all Sass files to Css for all sites once
        gulp dev 	    - compiles everything and watches files for changes. If changes occur, it recompiles
        gulp commands   - prints all available commands

###Typescript
We use Typescript as the primary language for the frontend. Typescript compiles to Javascript using the Typescript
compiler (tsc) and allows you to use types in a similar fashion to C# or Java. It also contains features of the next Javascript
editions (es6 & es7). In order to compile to Javascript you need node and the Typescript compiler. This process is
automated for us by using  by using gulp. When the site is running in production, the server fetches the compiled Javascript.

Typescript easily interops with existing Javascript libraries using definition files. In order to use existing libraries
you either need to declare them as global variables or using existing definition files. I highly reccomend you use
definition files from the Definitelytyped repository (see below).

[Typescript handbook](http://www.typescriptlang.org/Handbook)

[Typescript Definition files for existing Javascript libs](https://github.com/borisyankov/DefinitelyTyped)


####Typescript development plugins for different editors:
* Autocomplete server for various editors:
	[https://github.com/clausreinke/typescript-tools](https://github.com/clausreinke/typescript-tools)
* Vim:
	Typescript vim autocomplete and error highlighting plugin, highly reccomended. Depends on typescript-tools.
	[https://github.com/clausreinke/typescript-tools.vim](https://github.com/clausreinke/typescript-tools.vim)
* Sublime:
	Typescript Sublime plugin. Depends on typescript-tools.
	[https://github.com/Railk/T3S](https://github.com/Railk/T3S)
* Emacs:
	Typescript Emacs plugin. Depends on typescript-tools.
	[https://github.com/aki2o/emacs-tss](https://github.com/aki2o/emacs-tss)
* Eclipse:
	[http://typecsdev.com/](http://typecsdev.com/)
* Jetbrains IDE's:
	Various IDE's that have great support for Javascript/Typescript built in. I recommend Webstorm or Pycharm.
	[https://www.jetbrains.com/](https://www.jetbrains.com/)


###Sass
Sass is a superset of CSS which provides a reusable way of writing CSS. It allows for simple functions, ranges and variables.
Using Gulp we compile Sass to CSS in our build process when changes occur.

See [http://sass-lang.com/](http://sass-lang.com/)

