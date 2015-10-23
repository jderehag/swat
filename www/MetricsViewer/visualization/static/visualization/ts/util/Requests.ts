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
*
* Short description:
*/

///<reference path="../../lib/jquery/jquery.d.ts"/>
module Requests {
  export var urls = {
    get_subsystems: '/get_subsystems/',
    get_files_for_subsystem: '/get_files_for_subsystem/',
    get_functions_for_file: '/get_functions_for_file/',
    treemap: '/treemap/',
    treemap_data: '/treemap_data/',
    lineview: '/lineview/',
    lineview_data: '/lineview_data/',
    subsystem_csv_dumper: '/subsystem_csv_dumper/',
    metric_descriptions: '/metric_descriptions/',
    docs: '/docs/'
  }


  export interface ajax_wrapper_opts {
    type?: string
    async?: boolean
  }


  //As the event based system may cause things to change quickly via the UI, it may
  //call double initial requests because of missing data. If we instead check for the
  //already active deferreds, and return from this cache we avoid the double request problem.
  var deferred_cache = {}


  export var $ajax_wrapper = (url:string, query_params?, response_type="application/json",
      jqueryopts?:ajax_wrapper_opts):JQueryPromise<any> => {
    /**
     * Wrapper around $.ajax which is used primarily to cache data and preprocess it
     * Note that if the server replies with mimetype json, jquery will automagically parse it!
     * Parsing it twice will cause errors, so specify the json mimetype on server side.
     */
    var options = {
      // jQuery has a bias towards php and has adapted the encoding of data towards php frameworks
      // Use traditional to make it Django compatible.
      traditional: true,
      cache: true,
      //Default vals for the opts
      type: 'GET',
      async: true,
      //query params
      data: {}
    }
    if(query_params) Object.keys(query_params).forEach(param => options.data[param] = query_params[param])
    options.data["response_type"] = response_type
    if(jqueryopts) Object.keys(jqueryopts).forEach(opt => options[opt] = jqueryopts[opt])

    //Why serialized with json and not only url? Requests are different depending on the request parametetrs
    var serialized_opts = url + JSON.stringify(options)
    if(deferred_cache[serialized_opts]) {
      console.log("Returning cached deferred")
      return deferred_cache[serialized_opts]
    }

    else {
      console.log("Caching new deferred:", url, "query params:", query_params)
      var deferred = $.when($.ajax(url, options))
      deferred_cache[serialized_opts] = deferred

      // Shift the first row since we use csv compatible json output. The first row describes the rest
      deferred = deferred.then((data: any[]) => {
        console.info("Server data received for", url, query_params)
        if(data[0][0] !== "string") {
          new Error("The first row in dumped data should describe the other rows")
        }
        var removed_row = data.shift()
        console.info("Remvoing descriptive row", removed_row)
        return data
      })
      return deferred
    }
  }
}
