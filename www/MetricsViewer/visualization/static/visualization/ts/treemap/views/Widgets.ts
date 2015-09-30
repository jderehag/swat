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

///<reference path="../../../lib/mustache/mustache.d.ts"/>
///reference path="../models/Metrics.ts" />
///<reference path="../State.ts" />

module TreemapPackage {

  var template_select_size = $("#template_select_size").html()
  var template_select_color = $("#template_select_color").html()
  Mustache.parse(template_select_size)
  Mustache.parse(template_select_color)

  /**
   * Represents the `select` elements that allow you to select the size and color metrics for the treemap.
   * This object is created twice in the application, once for size and once for color. The only thing that
   * differentiates them is that they take a different string as input `(size|color)`.
   * @Todo: Refactor into two separate classes. It makes more sense conceptually.
   */
  export class SelectView extends Framework.EventAPI implements Framework.View {
    $e: JQuery = $("<div>")
    models: Models.Metric[]
    state: State
    template: string
    type: string

    constructor(models: Models.Metric[], state: State, type: string) {
      super()
      this.models = models
      this.state = state
      this.template = type == 'size' ? template_select_size : template_select_color
      this.type = type

      this.state.on('update', this, this.render.bind(this))
      this.$e.on('change', 'select', this.handle_option_change.bind(this))
      this.render()
    }

    render() {
      var metric = this.type == 'size' ? this.state.size_metric.name : this.state.color_metric.name
      this.$e.html(Mustache.render(this.template, { desc_list: this.models }))
      this.$e.find("select").val(metric)
      this.$e.appendTo(".select-boxes")
    }

    handle_option_change() {
      var selected_opt = this.$e.find('select').val()
      console.log("Updating metric", selected_opt)
      if (this.type == 'size') {
        this.state.size_metric = this.models.filter(metric => metric.name == selected_opt)[0]
      }
      else {
        this.state.color_metric = this.models.filter(metric => metric.name == selected_opt)[0]
      }
    }
  }


  /**
   * Represents a bootstrap style breadcrumb that is used for navigation
   * Listens for changes on the state object or the DOM `li` elements it generates and updates accordingly.
   */
  var breadcrumb_template = $("#breadcrumb_template").html()
  Mustache.parse(breadcrumb_template)
  export class BreadCrumbView extends Framework.EventAPI implements Framework.View {
    $e: JQuery = $("#breadcrumb-container")
    template = breadcrumb_template
    state: State

    constructor(state: State) {
      super()
      this.state = state
      this.state.on("update", this, this.render.bind(this))

      this.$e.on('click', '.root', this.handle_root_click.bind(this))
      this.$e.on('click', '.subsystem', this.handle_subsystem_click.bind(this))
      this.$e.on('click', '.file', this.handle_file_click.bind(this))
    }

    handle_root_click() {
      var cmp = this.state.current_component
      if (cmp.type == 'root') this.state.current_component = cmp
      else if (cmp.type == 'subsystem') this.state.current_component = cmp.parent
      else if (cmp.type == 'file') this.state.current_component = cmp.parent.parent
    }

    handle_subsystem_click() {
      var cmp = this.state.current_component
      if (cmp.type == 'subsystem') this.state.current_component = cmp
      else if (cmp.type == 'file') this.state.current_component = cmp.parent
    }

    handle_file_click() {
      var cmp = this.state.current_component
      if (cmp.type == 'file') this.state.current_component = cmp
    }

    render() {
      var data = {
        root: undefined,
        subsystem: undefined,
        file: undefined,
      }
      var cmp = this.state.current_component
      if (cmp.type == 'root') {
        data.root = cmp
      }
      else if (cmp.type == 'subsystem') {
        data.root = cmp.parent
        data.subsystem = cmp
      }
      else if (cmp.type == 'file') {
        data.root = cmp.parent.parent
        data.subsystem = cmp.parent
        data.file = cmp
      }
      this.$e.html(Mustache.render(this.template, data))
    }
  }

  /**
   * Represents the loader that blocks the UI when new data is loading
   * Listens for state update events.
   */
  export class LoaderView extends Framework.EventAPI implements Framework.View {
    $e = $('#loader')
    state: State

    constructor(state: State) {
      super()
      this.state = state
      this.$e.show()
      state.on('start_update', this, () => this.$e.show())
      state.on('update', this, () => this.$e.hide())
    }
  }
}
