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

///<reference path="../models/Components.ts"/>
///<reference path="views/ChartView.ts"/>
///<reference path="views/MetricButtonViews.ts"/>
///<reference path="views/TreeView.ts"/>
///<reference path="../framework/Model.ts"/>
///<reference path="../util/Requests.ts"/>

///<reference path="../../lib/jquery/fancytree/jquery.fancytree.d.ts"/>

module LineView {

  export class App {
    root_model = new Models.Root()
    active_cmps = new Framework.Collection<Models.Base>()
    active_metrics = new Framework.Collection<Models.Metric>()


    constructor() {

      var defer_subsystems = Requests.$ajax_wrapper('/get_subsystems/')
      var defer_metric_descs = Requests.$ajax_wrapper('/metric_descriptions/')

      $.when(defer_subsystems, defer_metric_descs).done((subsystem_result: any[], metrics_result: any[]) => {

        var subsystem_models = subsystem_result.map(json => {
          return new Models.Subsystem(json[0], json[1], this.root_model)
        })

        //These metrics cant be used in the lineview yet!
        var lineview_incompatible_metrics = ["effective_complexity", "revisions", "defect_density"]

        var metric_models = metrics_result
          .map(metric => new Models.Metric(metric))
          .filter(model => lineview_incompatible_metrics.indexOf(model.name) === -1)

        this.root_model.children = subsystem_models
        var metricpanelview = new MetricPanelView(metric_models, this.active_metrics)
        var treeview = new TreeView(this.root_model, this.active_cmps)
        var chartview = new ChartView(this.active_cmps, this.active_metrics)
        var exportCsvButton = new ExportCsvButtonView(this.active_cmps, this.active_metrics)
        var loader = new LoaderView(chartview)
      })
    }

  }
}


