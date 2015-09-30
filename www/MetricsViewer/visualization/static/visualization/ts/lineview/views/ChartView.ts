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

///<reference path="../../../lib/d3/d3.d.ts"/>
///<reference path="../../../lib/c3/js/c3.d.ts"/>
///<reference path="../../../lib/jquery/jquery.d.ts"/>
///<reference path="../../framework/Collection.ts"/>
///<reference path="../../framework/View.ts"/>
///<reference path="../../models/Components.ts"/>
///<reference path="../../models/Metrics.ts"/>
///<reference path="../../util/Requests.ts"/>
///<reference path="./MetricButtonViews.ts"/>
///<reference path="./Constants.ts"/>
///<reference path="../LineViewApp.ts"/>

/**
 * This file contains logic for the Lineview chart.
 * The chart listens to the collections of active components and active metrics and updates when they emit change
 * events. For every change, data is loaded into the chart. If data is missing, it requests new data from the server.
 */

module LineView {



  export interface dates_vals {
    dates: number[]
    values: number[]
  }



  /** json */
  export interface historical_server_data {
    [id: string]: {
      [metric: string]: {
        [date: string]: number
      }
    }
  }

  /**
   * The view responsible for updating the chart.
   * It tracks the `active_cmps` and `active_metrics` and calls `render()` whenever they emit change events. Likewise,
   * it emites `"start_update"` and `"end_update"` when it starts and finishes updating.
   */
  export class ChartView extends Framework.EventAPI implements Framework.View {
    $e = $('#chart-container')
    c3chart: C3.ChartAPI
    events = {
      start_update: 'start_update',
      end_update: 'end_update'
    }
    active_cmps: Framework.Collection<Models.Base>
    active_metrics: Framework.Collection<Models.Metric>


    constructor(cmps: Framework.Collection<Models.Base>, metrics: Framework.Collection<Models.Metric>) {
      super()
      this.active_cmps = cmps
      this.active_metrics = metrics

      this.active_cmps.on("change", this, this.render.bind(this))
      this.active_metrics.on("change", this, this.render.bind(this))

      this.c3chart = c3.generate(this.gen_c3_opts())
      this.render()
    }


    render() {
      this.trigger(this.events.start_update)
      if (this.active_cmps.arr.length == 0 && this.active_metrics.arr.length == 0) {
        setTimeout(() => {
          this.trigger(this.events.end_update)
          this.c3chart.unload()
        }, Constants.CHART_BUTTONS_TIMEOUT)
      }

      else {
        var deferreds: JQueryPromise<any>[] = []
        this.active_cmps.forEach(cmp => {
          this.active_metrics.arr.forEach(metric => {
            if (cmp.chart_data[metric.name] === undefined) {
              console.log("[ChartView]Missing chart data, loading from server", cmp.name, metric.name)

              var def = Requests.$ajax_wrapper('/lineview_data/', {
                id: cmp.id,
                type: cmp.type,
                metric: metric.name
              })
              def.then(chart_data => {
                cmp.chart_data[metric.name] = chart_data
              })
              deferreds.push(def)
            }
          })
        })

        $.when.apply($, deferreds).then(() => {
          var data = this.format_c3_data(this.active_cmps.arr, this.active_metrics.arr)
          setTimeout(() => {
            this.c3chart = c3.generate(data)
            this.trigger(this.events.end_update)
          }, Constants.CHART_BUTTONS_TIMEOUT)
        })
      }
    }


    format_c3_data(cmps: Models.Base[], metrics: Models.Metric[]) {
      var opts = this.gen_c3_opts()

      var metric_names = metrics.map(metric => metric.name)
      if (metric_names.indexOf("defect_modifications") > -1 && metric_names.length >= 2) {
        opts.axis.y2.show = true
      }

      cmps.forEach(cmp => {
        metrics.forEach(metric => {
          var interval = metric.histogram_interval
          var line_name = cmp.name + " - " + metric.name
          var ddd: any // It's actually [dates_vals] but TSS tools use old compiler so type messes up

          if (metric.chart_type == 'line') {
            ddd = this.format_line_data(cmp.chart_data[metric.name])
          }
          else {
            ddd = this.format_histogram_data(cmp.chart_data[metric.name], interval)
          }

          var xvals:any[] = [line_name + "-x"].concat(ddd.dates)
          var yvals:any[] = [line_name].concat(ddd.values)

          opts.data.columns.push(xvals, yvals)
          opts.data.xs[line_name] = line_name + "-x"

          //If we have defect_modifications and at least [defect_modifications + other metric] 
          //use defect_modifications on the right axis
          if (metric.name == 'defect_modifications' && opts.axis.y2.show) {
            opts.data.axes[line_name] = 'y2'
          }
          else {
            opts.data.axes[line_name] = 'y'
          }

          if (metric.chart_type == 'line') {
            opts.data.types[line_name] = 'line'
          }
          else {
            opts.data.types[line_name] = 'area-step'
          }

        })
      })
      console.log("opts", opts)
      return opts
    }

    /**
     * Generates C3 API options. It returns an object that conforms to the C3 API.
     * See `http://c3js.org/reference.html`
     */
    gen_c3_opts(): C3.Options {
      return {
        //C3 doesn't support jquery selectors so pass either strings or html-els
        bindto: document.getElementById(this.$e.find('#chart').attr('id')),
        axis: {
          x: {
            type: 'timeseries',
            tick: {
              format: '%Y-%m-%d'
            }
          },
          y2: {
            show: false
          }
        },
        data: {
          columns: [],
          xs: {},
          types: {},
          axes: {}
        }
      }
    }


    /**
     * Formats data for the C3 chart in linear diagram style.
     */
    format_line_data = (metric_data: [[number, number]]): dates_vals => {
      return {
        // C3 only takes milis
        dates: metric_data.map(entry => entry[0] * 1000),
        values: metric_data.map(entry => entry[1])
      }
    }

    /**
     * Formats data for the C3 chart in a barchart or areachart style.
     * This function splits the data up in intervals and accumulates data for all entries between specific intervals where:
     * interval.startdate < data_entry.date < interval.enddate
     * It returns `dates_vals` similar to the line diagram data, but for summarized date periods.
     */
    format_histogram_data = (metric_data: [[number, number]], interval: number): dates_vals  => {
      /*
      */

      // In case we have no dates and vals go no further
      var returnobj: dates_vals = {
        dates: [],
        values: []
      }
      if (metric_data.length === 0) {
        return returnobj
      }

      var create_interval = (start: number, end: number): { start: number; end: number; val: number } => {
        return {
          start: start,
          end: end,
          val: 0
        }
      }

      var sorted_data = metric_data.sort((a, b) => {
        return a[0] - b[0]
      })
      var min_date = sorted_data[0][0]
      var max_date = sorted_data[sorted_data.length - 1][0]
      // Intervals in milisecs
      var interval_size = 2629743.83 * interval
      var no_of_intervals = Math.ceil((max_date - min_date) / interval_size)
      var intervals: Array<{ start: number; end: number; val: number }> = []
      // start - 1 to ensure that the first data_arr entry is included since the interval
      // ensures that the data entry must be between, but not equal to, it's boundries
      var start = min_date - 1

      for (var i = 0; i < no_of_intervals; i++) {
        intervals.push(create_interval(start, start + interval_size))
        start += interval_size
      }

      // Todo: Optimize if neccesary. It turns out that using traditional for loops
      // instead of forEach significantly improves speed, so we might not need smarter code
      for (var j = 0; j < sorted_data.length; j++) {
        for (var k = 0; k < intervals.length; k++) {
          var data_entry = sorted_data[j]
          var interval_entry = intervals[k]
          if (interval_entry.start < data_entry[0] && interval_entry.end > data_entry[0]) {
            interval_entry.val += data_entry[1]
          }
        }
      }
      returnobj.dates = intervals.map(entry => entry.start * 1000)
      returnobj.values = intervals.map(entry => entry.val)
      return returnobj
    }
  }


  /**
   * A loader object which is show while the chart is in updating state.
   * Once the chart leaves the updating state the loader is hidden.
   */
  export class LoaderView extends Framework.EventAPI implements Framework.View {
    $e: JQuery = $('#loader')
    chartview: ChartView

    constructor(chartview: ChartView) {
      super()
      this.chartview = chartview
      this.chartview.on(this.chartview.events.start_update, this, () => this.$e.show())
      this.chartview.on(this.chartview.events.end_update, this, () => this.$e.hide())
    }
  }

}

