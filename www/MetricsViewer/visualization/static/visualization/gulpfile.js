/*
Copyright (C) 2015 - Dani Hodovic <dani.hodovic@ericsson.com> for Ericsson AB
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions
and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

**************************    THIS LINE IS 120 CHARACTERS WIDE - DO *NOT* EXCEED 120 CHARACTERS!    *******************
*/

var path = require('path')
var spawn = require('child_process').spawn
var gulp = require('gulp')
var es = require('event-stream')
var livereload = require('gulp-livereload')
var sass = require('gulp-sass')
var autoprefixer = require('gulp-autoprefixer')
var notifier = require('node-notifier')

var sass_src = 'sass/*.scss'
var sass_out = 'bin/css'
var js_out = 'bin/js'

var models_dir = 'ts/models/*.ts'
var framework_dir = 'ts/framework/*.ts'
var util_dir = 'ts/util/*.ts'

var treemap_dir = "ts/treemap/**/*.ts"
var treemap_src = "ts/treemap/TreemapApp.ts"
var treemap_out = "treemap.bin.js"

var lineview_dir = 'ts/lineview/**/*.ts'
var lineview_src = 'ts/lineview/LineViewApp.ts'
var lineview_out = 'lineview.bin.js'


gulp.task('lineview', function() {
  native_tsc_task(lineview_src, lineview_out, js_out)
})

gulp.task('treemap', function() {
  native_tsc_task(treemap_src, treemap_out, js_out)
})

gulp.task('watch-lineview', function() {
  livereload.listen()
  native_tsc_task(lineview_src, lineview_out, js_out, true)
})

gulp.task('watch-treemap', function() {
  livereload.listen()
  native_tsc_task(treemap_src, treemap_out, js_out, true)
})

gulp.task('sass', function() {
  sass_task(sass_src, sass_out)
})

gulp.task('watch-sass', function() {
  livereload.listen()
  gulp.watch([sass_src], ['sass'])
})

gulp.task('dev', ['treemap', 'lineview', 'sass', 'watch-lineview', 'watch-treemap', 'watch-sass'])

gulp.task('commands', function() {
  console.log('***************************************************************************************')
  console.log('Usage: gulp <command>')
  console.log('The following gulp builds are available:')
  console.log('commands - Prints this')
  console.log('treemap  - Compile the treemap typescript files to javascript')
  console.log('lineview - Compiles the lineview typescript files to javascript')
  console.log('sass     - Compiles Sass to Css')
  console.log('dev      - Compiles everything and runs file watchers that recompile on change')
  console.log('By default running <gulp> will compile all files, i.e run treemap, lineview and sass')
  console.log('***************************************************************************************')
})

gulp.task('default', ['treemap', 'lineview', 'sass'])

/////////////////////////////
// Wrapper build functions //
/////////////////////////////
function native_tsc_task(main_file, out_file, out_dir, watch) {
  var maybe_slash = out_dir[out_dir.length] != '/' ? '/' : ''

  var opts = [
    '--out', out_dir + maybe_slash + out_file,
    '--target', 'es5',
    '--noEmitOnError',
    '--sourceMap',
    main_file
  ]
  if(watch) opts.push('--watch')

  var child = spawn('./node_modules/typescript/bin/tsc', opts)
  child.stdout.on('data', handle_tsc_output)
}

var error_regex = new RegExp('error', 'i')
var success_regex = new RegExp('compilation complete', 'i')

function handle_tsc_output(buffer) {
  var str = buffer.toString()
  var title = ''
  var msg = ''
  var error = error_regex.test(str)
  var success = success_regex.test(str)

  if (error) {
    var strs = str.split('\n')
    title += strs[0]
    msg = strs[1]
    console.error("ERROR:", strs[0])
  } 
  else if (success) {
    title += 'Compilation complete'
    livereload.reload()
  }

  if (error || success) {
    notifier.notify({
      title: title,
      message: msg.substr(0, 281) + "..."
    })
  }
}


function sass_task(file, out) {
  gulp.src(file)
    .pipe(sass())
    .on('error', notify_and_handle_error)
    .pipe(autoprefixer())
    .pipe(gulp.dest(out))
    .pipe(livereload())
    .pipe(notify_success())
}


function notify_success() {
  function transform(file, cb) {
    var basename = file.path.substr(file.path.lastIndexOf('/') + 1)
    notifier.notify({
      title: 'Success',
      message: basename
    })

    cb(null, file);
  }

  return es.map(transform);
}

function notify_and_handle_error(err) {
  console.log(err.message)
  var relevant_error_msg = err.message.substr(
    err.message.lastIndexOf('/') + 1)

  notifier.notify({
    title: relevant_error_msg,
    message: err.message
  })
  this.emit("end")
}
