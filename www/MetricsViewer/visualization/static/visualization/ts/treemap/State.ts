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

///<reference path="../framework/Model.ts"/>
///<reference path="../models/Components.ts"/>
///<reference path="../models/Metrics.ts"/>
///<reference path="DataLoader.ts"/>

module TreemapPackage {

  export interface state_attrs {
    current_component?: Models.Parent
    size_metric?: Models.Metric
    color_metric?: Models.Metric
  }

  export class State extends Framework.EventAPI {
    attrs:state_attrs = {}
    existing_metrics:Models.Metric[]

    constructor(cmp:Models.Parent, metrics:Models.Metric[],
                size_metric:Models.Metric, color_metric:Models.Metric) {
      super()
      this.existing_metrics = metrics
      this.attrs.current_component = cmp
      this.attrs.size_metric = size_metric
      this.attrs.color_metric = color_metric

      this.on('update', this, () => {
        console.log("Updating State...",
        this.attrs.current_component,
        this.attrs.size_metric,
        this.attrs.color_metric)
      })

      this.update()
    }

    get size_metric():Models.Metric {
      return this.attrs.size_metric
    }

    get color_metric():Models.Metric {
      return this.attrs.color_metric
    }

    get current_component():Models.Parent {
      return this.attrs.current_component
    }

    set size_metric(metric:Models.Metric) {
      this.trigger('start_update')
      this.attrs.size_metric = metric
      this.update()
    }

    set color_metric(metric:Models.Metric) {
      this.trigger('start_update')
      this.attrs.color_metric = metric
      this.update()
    }

    set current_component(cmp:Models.Parent) {
      this.trigger('start_update')
      this.attrs.current_component = cmp
      console.log("State: Setting current component", cmp)
      this.update()
    }

    update() {
      var cmp = this.current_component
      var done_children = $.Deferred<any>()
      // Handle special case of entering a file with effective complexity,
      // which doesn't exist for that level so normal complexity is returned
      // Set it to a silent update using .attrs because we don't need to update twice
      if (cmp.type == 'file') {
        var complexity = this.existing_metrics.filter(
            metric => metric.name == 'cyclomatic_complexity')[0]
        if (this.size_metric.name == 'effective_complexity') {
          this.attrs.size_metric = complexity
        }
        else if (this.color_metric.name == 'effective_complexity') {
          this.attrs.color_metric = complexity
        }
      }

      if (cmp.children.length == 0) {
        console.log('State loading children...')
        cmp.load_children().then(() => done_children.resolve())
      }
      else done_children.resolve()

      done_children.then(() => {
        var size_dfd = DataLoader.load_data(this.size_metric, this.existing_metrics, cmp.children[0])
        var color_dfd = DataLoader.load_data(this.color_metric, this.existing_metrics, cmp.children[0])

        $.when(size_dfd, color_dfd).then(() => {
          this.trigger('update', this, cmp.children)
        })
      })
    }
  }

}
