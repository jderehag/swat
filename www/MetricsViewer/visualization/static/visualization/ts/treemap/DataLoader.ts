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

///<reference path="TreemapApp.ts"/>
module TreemapPackage {
  export module DataLoader {


    export var load_data = (metric:Models.Metric,
                            metrics:Models.Metric[],
                            first_child:Models.Base) => {

      var promise:JQueryPromise<any>

      if (metric.name == Models.METRIC_NAMES.changerate) {
        promise = load_changerate(metrics, first_child)
      }
      else if (metric.name == Models.METRIC_NAMES.risk_assessment) {
        //Todo
      }

      else {
        promise = load_db_metric(metric, first_child)
      }

      return promise
    }

    var load_db_metric = (metric:Models.Metric, component:Models.Base) => {
      /**
       * If the child data has been loaded, it returns a resolved deferred
       * Otherwise it loads data and caches it
       */
      if (component.treemap_data[metric.name] !== undefined) {
        return $.Deferred().resolve()
      }

      var metric_deferred = get_deferred('/treemap_data/', component.parent, metric)
      // The children are a deferred...so we have to pass it through a when
      var promise = $.when(metric_deferred)
      promise.then((metric_data:[[string, number, number]]) => {
        var children = component.parent.children

        //There are probably metrics for each model
        if(metric_data.length == children.length) {
          for (var i = 0; i < children.length; i++) {
            var child = children[i]
            var metric_entry = metric_data[i]
            assert_ids_match(child.id, metric_entry[1])
            child.treemap_data[metric.name] = metric_entry[2] || 0 //In case of db null
          }
        }

        else {
          console.log("Local and server ids do not match, attempting to index...")
          var data_ids = metric_data.map(entry => entry[1])
          children.forEach(child => {
            var index = data_ids.indexOf(child.id)
            // The child has data returned
            if(index > -1) {
              child.treemap_data[metric.name] = metric_data[index][2] || 0 //In case of db null
            }
            else {
              child.treemap_data[metric.name] = 0
            }
          })
        }
      })
      return promise
    }


    var load_changerate = (metrics:Models.Metric[], component:Models.Base) => {
      /**
       * If the dependencies for each metric are already loaded, it returns a resolved
       * deferred.
       * Otherwise it calls load_db_metric() to load new data, cache it, and then aggregates based
       * on that data
       */
      var dependencies = [Models.METRIC_NAMES.added, Models.METRIC_NAMES.changed,
        Models.METRIC_NAMES.deleted]

      var missing_metrics: Models.Metric[] = dependencies
        //Filter missing ones
        .filter(name => component.treemap_data[name] === undefined)
        //Map to real metric models
        .map(name => metrics.filter(metric => metric.name == name)[0])

      if (missing_metrics.length == 0) {
        return $.Deferred().resolve()
      }

      var promises = missing_metrics.map(metric => load_db_metric(metric, component))
      var promise = $.when.apply($, [component.parent.children].concat(promises))
      promise.then((children:Models.Base[]) => {
        children.forEach(child => aggregate_changerate(child))
      })

      return promise
    }


    var aggregate_changerate = (cmp:Models.Base) => {
      var data = cmp.treemap_data
      data['changerate'] = data['added'] + data['changed'] + data['deleted']
    }


    var get_deferred = (url, component, metric) => {
      return Requests.$ajax_wrapper(url, $.extend(component.toJSON(), {'metric': metric.name}))
    }

    var assert_ids_match = (...ids:number[]) => {
      var first = ids[0]
      var filtered = ids.filter(id => id === first)
      if (ids.length != filtered.length) {
        throw new Error("Server ID and local ID do not match ids: " + ids)
      }
    }

  }
}

