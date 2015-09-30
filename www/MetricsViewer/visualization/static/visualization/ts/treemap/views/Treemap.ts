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

///<reference path="../../../lib/jquery/jquery.d.ts" />
///<reference path="../../../lib/d3/d3.d.ts" />
///<reference path="../../framework/View.ts" />
///<reference path="../../framework/Event.ts" />
///<reference path="../TreemapApp.ts" />
///<reference path="../State.ts" />
module TreemapPackage {
  declare var d3plus:any

  export class Treemap extends Framework.EventAPI implements Framework.View {
    $e:JQuery = $('#treemap')
    model:State
    contextmenu_view:ContextMenuView

    constructor(state:State) {
      super()
      this.model = state
      this.contextmenu_view = new ContextMenuView(state)

      this.model.on('update', this, (evtname:string, data:[State, Models.Base[]]) => {
        this.render.apply(this, data)
      })
      this.$e.on('click', '.d3plus_data', this.handle_click.bind(this))
      this.$e.on('contextmenu', '.d3plus_data', this.handle_contextmenu.bind(this))
    }

    render(state:State, children:Models.Base[]):void {
      var data = this.adapt_data_for_d3(state, children)

      var color_scale = this.create_color_scale(children, state.color_metric.name)
      d3plus.viz()
        .container('#' + this.$e.attr("id"))
        .type('tree_map')
        .id('id')
        .text('name')
        .tooltip({
          'anchor': 'top left',
          'value': ['size_value', 'color_value']
        })
        .data(data)
        .size({
          'value': 'size_value',
          'threshold': false,
          'rendering': 'crispEdges'
        })
        .color(function (d3_cmp:any) {
          return color_scale(d3_cmp.color_value)
        })
        .format({
          text: text => {
            // Text is the key passed to the object
            if (text === 'size_value') {
              return state.size_metric.name
            } else if (text === 'color_value') {
              return state.color_metric.name
            } else {
              return text
            }
          },
          number: (number, key) => {
            if (number < 0.1) {
                return number;
            } else {
                return d3plus.number.format(number, key);
            }
          }
        })
        .draw()
    }

    handle_click(event:JQueryEventObject) {
      var current_cmp = this.model.current_component
      if (['root', 'subsystem'].indexOf(current_cmp.type) != -1) {
        var id = $(event.target).data('component_id')
          var cmp = <Models.Parent> current_cmp.children.filter(child => child.id == id)[0]
          this.model.current_component = cmp
      }
    }

    handle_contextmenu(event:JQueryEventObject) {
      event.preventDefault()
      var id = $(event.target).data('component_id')
        var cmp = this.model.current_component.children.filter(child => child.id == id)[0]
        this.contextmenu_view.last_clicked_cmp = cmp
        this.contextmenu_view.$e.css({
          // offsetX is not supported in FF...
          left: (event.offsetX || event.pageX - this.$e.offset().left),
          top: (event.offsetY || event.pageY - this.$e.offset().top),
          display: "block"
        })
    }

    adapt_data_for_d3(state:State, children:Models.Base[]) {
      var adapted = children.map((child) => {
        var o = {}
        o["id"] = child.id
        o["name"] = child.name
        o["abspath"] = child["abspath"]
        o["size_value"] = child.treemap_data[state.size_metric.name]
        o["color_value"] = child.treemap_data[state.color_metric.name]
        return o
      })
      return adapted
    }

    create_color_scale(children:Models.Base[], color_metric:string) {
      var max_cmp = children.reduce((ch1, ch2) => {
        var v1 = ch1.treemap_data[color_metric]
        var v2 = ch2.treemap_data[color_metric]
        return v1 > v2 ? ch1 : ch2
      })

      var val = max_cmp.treemap_data[color_metric]
      var max
      if (color_metric == 'effective_complexity') {
        max = 1.0
      }
      else {
        max = val > 15 ? val : 15
      }
      return d3.scale.linear().range(['green', 'red']).domain([0, max])
    }

  }


  class ContextMenuView extends Framework.EventAPI implements Framework.View {
    $e:JQuery = $('#contextMenu')
    state:State
    last_clicked_cmp:Models.Base

    constructor(state:State) {
      super()
      this.state = state
      this.$e.on('click', '.up-one-level', () => this.handle_up_one_level())
      this.$e.on('click', '.view-chart', () => this.handle_view_chart())
      this.$e.on('click', '.copy-path', () => this.handle_copy_path())
      this.$e.on('click', '.remove', () => this.handle_remove_component())
      this.$e.on('click', '.reset', () => this.handle_reset())
      $(document).on('click', this.handle_hide.bind(this))

      /* Todo: Fix */
      this.$e.find('.view-chart').hide()
    }

    handle_hide(event:JQueryEventObject) {
      if (this.$e.is(':visible')) {
        //If right click
        if (event.which == 1)
          this.$e.hide()
      }
    }

    handle_up_one_level() {
      var grandparent = this.last_clicked_cmp.parent.parent
      if (grandparent !== undefined) {
        this.state.current_component = grandparent
      }
    }

    handle_view_chart() {

    }

    handle_copy_path() {
      var msg:string
      if (this.last_clicked_cmp["abspath"]) msg = "Absolute path: Ctrl+C, Enter"
      else msg = "The component has no absolute path"
      window.prompt(msg, this.last_clicked_cmp["abspath"] || "None found")
    }

    handle_remove_component() {
      var removed_cmp = this.last_clicked_cmp
      this.state.current_component.children.forEach((child, index, children) => {
          if (child.id == removed_cmp.id) {
            children.splice(index, 1)
            this.state.update()
          }
      })
    }

    handle_reset() {
      // TODO: Reset to cached copy
      var cmp = this.last_clicked_cmp
      this.state.current_component.children = []
      this.state.update()
    }
  }


}
