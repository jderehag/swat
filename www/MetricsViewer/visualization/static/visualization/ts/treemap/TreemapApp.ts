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
///<reference path="./views/Widgets.ts" />
///<reference path="./views/Treemap.ts" />
///<reference path="./State.ts" />
///<reference path="../util/Requests.ts" />

module TreemapPackage {

  export class TreemapApp {

    constructor(metrics: any[]) {
      var defer_metrics_descs = Requests.$ajax_wrapper('/metric_descriptions/')
      $.when(defer_metrics_descs).done((descs: any[]) => {

        var metric_models = descs.map(metric => new Models.Metric(metric))
        var nloc_model = metric_models.filter(model => model.name == 'nloc')[0]
        var defect_model = metric_models.filter(model => model.name == 'defect_modifications')[0]

        var state = new State(new Models.Root(), metric_models, nloc_model, defect_model)
        var color_select_view = new SelectView(metric_models, state, 'color')
        var size_select_view = new SelectView(metric_models, state, 'size')
        var breadcrumb = new BreadCrumbView(state)
        var loader = new LoaderView(state)
        var treemap = new Treemap(state)
      })
    }
  }


}

