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

///<reference path="../../../lib/jquery/jqueryui.d.ts"/>
///<reference path="../../../lib/mustache/mustache.d.ts"/>
///<reference path="../../framework/Event.ts"/>
///<reference path="../../framework/View.ts"/>
///<reference path="../../framework/Collection.ts"/>
///<reference path="../../models/Metrics.ts"/>
///<reference path="../../models/Components.ts"/>
///<reference path="../views/Constants.ts"/>

module LineView {

  export class MetricPanelView extends Framework.EventAPI implements Framework.View {
    $e = $('.metricpanel-view')
    button_views: MetricButtonView[] = []

    constructor(metrics: Models.Metric[], active_metrics: Framework.Collection<Models.Metric>) {
      super()
      metrics.forEach((metric) => {
        var button_view = new MetricButtonView(metric, active_metrics)
        this.button_views.push(button_view)
      })
      this.render()
    }

    render() {
      this.$e.find('.metricrow-container').empty()
      this.button_views.forEach((button_view) => {
        this.$e.find('.metricrow-container').append(button_view.$e)
      })

      var defects_btn = this.button_views.filter(btn => btn.model.name == 'defect_modifications')[0]
      var nloc_btn = this.button_views.filter(btn => btn.model.name == 'nloc')[0]
      // Set initially clicked btns
      defects_btn.$e.find('.histogram-button').click()
      nloc_btn.$e.find('.line-button').click()
    }
  }


  var button_template = $('#template_metricrow').html()
  export class MetricButtonView extends Framework.EventAPI implements Framework.View {
    $e = $('<tr>')
    template = button_template
    model: Models.Metric
    active_metrics: Framework.Collection<Models.Metric>

    slider_attrs = {
      min: 1,
      max: 36,
      step: 1,
      value: 3,
      title: () => "interval of " + this.slider_attrs.value + " months"
    }

    constructor(model: Models.Metric, active_metrics) {
      super()
      this.model = model
      this.active_metrics = active_metrics
      this.bind_events()
      this.render()
      this.model.histogram_interval = this.slider_attrs.value
    }

    render = () => {
      var el = Mustache.render(this.template, this.model.toTemplate())
      this.$e.html(el)
      this.$e.find('.slider').attr(this.slider_attrs).hide()
    }

    bind_events = () => {
      // Whenever our model changes, cause this object to change.
      this.model.on('change', this, this.trigger.bind(this))
      this.$e.on('click', '.line-button', this.handle_btn_group.bind(this, 'line'))
      this.$e.on('click', '.histogram-button', this.handle_btn_group.bind(this, 'histogram'))
      this.$e.on('click', '.none-button', this.handle_btn_group.bind(this, 'none'))
      this.$e.on('change', '.slider',() => this.handle_slider_change())
    }

    /**
     * Method that handles the changes of slider intervals. It assigns the histogram value to the model through a setter
     * which causes the model to update and in turns causes this object to change.
     */
    handle_slider_change() {
      var val = this.$e.find('.slider').prop('value')
      this.$e.find('.slider').prop('title', "interval " + val + " months")
      this.model.histogram_interval = parseInt(val)
    }

    handle_btn_group(active) {
      if (active === 'histogram') {
        this.$e.find('.slider').show(Constants.CHART_BUTTONS_TIMEOUT)
      }
      else if (active === 'line') {
        this.$e.find('.slider').hide(Constants.CHART_BUTTONS_TIMEOUT)
      }
      else {
        this.$e.find('.slider').hide(Constants.CHART_BUTTONS_TIMEOUT)
      }

      if (active === 'line' || active === 'histogram') {
        this.model.chart_type = active
        if(!this.active_metrics.includes(metric => metric.name === this.model.name)) {
          this.active_metrics.push(this.model)
        }
      }
      else {
        this.model.attrs.chart_type = 'none'
        this.active_metrics.remove(model => model.name == this.model.name)
      }
    }
  }


  export class ExportCsvButtonView extends Framework.EventAPI implements Framework.View {
    $e = $('#export_to_csv')
    links_modal: CSVLinksModal

    constructor(cmps: Framework.Collection<Models.Base>, metrics: Framework.Collection<Models.Metric>) {
      super()
      this.links_modal = new CSVLinksModal(cmps, metrics)
      this.$e.on('click',(event: Event) => {
        event.preventDefault()
        let urls = this.links_modal.get_urls(cmps, metrics)
        this.links_modal.show_modal()
      })
    }
  }

  export class CSVLinksModal extends Framework.EventAPI implements Framework.View {
    // This container is appended to the bottom of the page with a height of 0
    $e = $('<div>')
    template = $('#template_links').html()
    cmps: Framework.Collection<Models.Base>
    metrics: Framework.Collection<Models.Metric>
    constructor(cmps: Framework.Collection<Models.Base>, metrics: Framework.Collection<Models.Metric>) {
      super()
      this.cmps = cmps
      this.metrics = metrics
      this.render()
      $('body').append(this.$e)
    }

    render() {
      let links = this.get_urls(this.cmps, this.metrics)
      this.$e.html(Mustache.render(this.template, { links: links }))
    }

    show_modal() {
      this.render()
      let bootstrap_modal: any = this.$e.find('.modal')
      bootstrap_modal.modal('show')
    }

    get_urls(cmps: Framework.Collection<Models.Base>, metrics: Framework.Collection<Models.Metric>) {
      let urls = []

      for(let cmp of this.cmps.arr) {
        for(let metric of this.metrics.arr) {
          let url_params = {
            id: cmp.id,
            type: cmp.type,
            metric: metric.name,
            response_type: 'text/csv'
          }

          let url_obj = {
            url: this.create_url('/lineview_data/', url_params),
            cmp: cmp,
            metric: metric
          }
          urls.push(url_obj)
        }
      }
      return urls
    }

    create_url(baseurl: string, keywords: {}) :string {
      baseurl += "?"
      Object.keys(keywords).forEach(key => baseurl += key + "=" + keywords[key] + "&")
      //Remove last &
      return baseurl.substr(0, baseurl.length - 1)
    }
  }
}

