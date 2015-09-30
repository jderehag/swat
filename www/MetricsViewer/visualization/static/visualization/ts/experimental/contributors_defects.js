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

/* eslint-env browser */
/* global d3 */


var g_id = 0

function EventCls() {
  var self = {}
  self.__id = ++g_id
  self.eventCache = {}
  self.on = on
  self.off = off
  self.trigger = trigger


  function on(other_ev_instance, str_or_strarr, callback) {
    assert(other_ev_instance !== undefined)
    assert(typeof callback === 'function')

    var id_entry = self.eventCache[other_ev_instance.__id] || (self.eventCache[other_ev_instance.__id] = {})

    if (Array.isArray(str_or_strarr)) {
      str_or_strarr.forEach(function(str) {
        addEvent(id_entry, str, callback)
      })
    }
    else if (typeof str_or_strarr === 'string') {
      addEvent(id_entry, str_or_strarr, callback)
    }
    else {
      throw "The event string attached must be a string or an array of strings"
    }
  }


  function addEvent(id_entry, str, callback) {
    assert(typeof str === 'string')
    var callback_arr = id_entry[str] || (id_entry[str] = [])
    callback_arr.push(callback)
  }


  function off(str, other_ev_instance) {}


  function trigger(str) {
    Object.keys(self.eventCache).forEach(function(id) {
      var id_entry = self.eventCache[id] || (self.eventCache[id] = {})
      var callback_arr = id_entry[str] || (id_entry[str] = [])
      for (var i = 0; i < callback_arr.length; i++) {
        callback_arr[i]()
      }
    })
  }

  return self
}


function State(startdate, enddate, srcfiles) {
  var self = EventCls()
  self.on = on_ensure_prop_exists(self.on)
  self.attrs = {
    startdate: startdate,
    enddate: enddate,
    srcfiles: srcfiles,
    show_circles: true,
    show_path: false,
    severity: []
  }
  Object.keys(self.attrs).forEach(addAttr)

  function on_ensure_prop_exists(original_on) {
    /**
     * Wrapper method for `EventCls.on` that ensures the listening event prop exists in `self.attrs`
     */
    return function() {
      var args = Array.prototype.slice.call(arguments)

      if (typeof args[1] === 'string') {
        var prop_str = args[1].split(":")[1]
        assert(self.attrs[prop_str] !== undefined, "Attached listener for a property that doesn't exist: " + prop_str)
      }
      else if (Array.isArray(args[1])) {
        args[1].forEach(function(ev_str) {
          var prop_str = ev_str.split(":")[1]
          assert(self.attrs[prop_str] !== undefined, "Attached listener for a property that doesn't exist: " + prop_str)
        })
      }
      // Call the original on from `EventCls` to handle the callback attachment
      return original_on.apply(self, args)
    }
  }

  /**
   * Dynamically add setters and getters that trigger events for a specific key
   * The getters/setters are attached to `self`
   */
  function addAttr(key) {
    Object.defineProperty(self, key, {
      get: function() {
        return self.attrs[key]
      },

      set: function(value) {
        if (value !== self.attrs[key]) {
          self.attrs[key] = value
          self.trigger('change')
          self.trigger('change:' + key)
        }
      }
    })
  }


  return self
}



/**
 * Widgets
 */

function Tooltip_V() {
  var self = EventCls()
  self.template = document.querySelector("#template-tooltip").innerHTML
  Mustache.parse(self.template)
  self.$e = d3.select("#chart").append("div")
    .attr("class", "chart-tooltip")
    .style("opacity", 0)
  self.render = render
  self.hide = hide


  function render(d, xattr, yattr) {
    var data = {
      attributes: Object.keys(d).map(function(key) {
        return {
          key: key,
          value: d[key],
          active: key === xattr || key === yattr ? true : false
        }
      })
    }

    self.$e.transition()
      .duration(200)
      .style("opacity", 1)
    self.$e.html(Mustache.render(self.template, data))
      .style("left", (d3.event.pageX + 10) + "px")
      .style("top", (d3.event.pageY - 30) + "px")
  }


  function hide(d) {
    self.$e.transition()
      .duration(200)
      .style("opacity", 0)
  }


  return self
}


function ShowLine_V(state) {
  var self = EventCls()
  self.$e = d3.select('#show-linechart')
  self.$e.on('change', handle_change)


  function handle_change(event) {
    var checked = d3.select(this).property("checked")
    if (checked) {
      state.show_path = true
    }
    else {
      state.show_path = false
    }
  }


  return self
}

function ShowCircles_V(state) {
  var self = EventCls()
  self.$e = d3.select('#show-scatterchart')
  self.$e.on('change', handle_change)


  function handle_change(event) {
    var checked = d3.select(this).property("checked")
    if (checked) {
      state.show_circles = true
    }
    else {
      state.show_circles = false
    }
  }


  return self
}

function Srcfiles_V(state) {
  var self = EventCls()
  self.$e = d3.select("#srcfiles")
  self.$e.on('change', handle_change)


  function handle_change(event) {
    var checked = d3.select(this).property("checked")
    if (checked) {
      state.srcfiles = true
    }
    else {
      state.srcfiles = false
    }
  }


  return self
}

function SelectYears_V(state) {
  var self = EventCls()
  self.$e = d3.select("#select-year")
  self.$e.on('change', handle_change)


  function handle_change(event) {
    var year_diff = parseInt(self.$e.property("value"))
    var now = new Date()
    var prev_year
    if (year_diff === "all") {
      //Since 1970
      prev_year = new Date(0)
    }
    else {
      prev_year = new Date(now.getFullYear() - year_diff, now.getMonth(), now.getDay())
    }
    //Silent via `attrs` to avoid multiple rerenderings
    state.attrs.startdate = prev_year
    state.attrs.enddate = now
    state.trigger('change:enddate')
  }


  return self
}


function SeverityBtns_V(state) {
  var self = EventCls()
  self.$e = d3.select("#select-severity")
  self.$e.selectAll('.severity-btn').on('change', handle_change)

  function handle_change() {
    var $elem = d3.select(this)
      //id is `severty-<x>`
    var value = $elem.attr("id").split("-")[1]
    var new_severity

    if ($elem.property("checked")) {
      // Can't use push/splice because these don't trigger getters/setters and changes
      new_severity = state.severity.concat(value)
      state.severity = new_severity
    }
    else {
      new_severity = state.severity.filter(function(item) {
        return item !== value
      })
      state.severity = new_severity
    }
  }

  return self
}


function Chart_V(state, tooltip_V, dataset) {
  var self = EventCls()
  self.$e = d3.select('#chart')
  self.render = render

  state.on(self, 'change:srcfiles', show_srcfiles)

  var margin = {
    top: 40,
    right: 40,
    bottom: 40,
    left: 40
  }
  var width = 1200 - margin.left - margin.right
  var height = 700 - margin.top - margin.bottom

  /*
   * Action handlers
   */
  function show_srcfiles() {
    var data
    if (state.srcfiles) {
      var valid_extensions = ["c", "cc", "cpp"]
      data = dataset.filter(function(entry) {
        var extension = entry.file.split(".").pop()
        return valid_extensions.indexOf(extension) > -1
      })
    }
    else {
      data = dataset
    }
    self.render(data, "contributors_tr", "defects_abc")
  }

  /*
   * Chart rendering functions 
   */
  function render(data, xattr, yattr) {
    var $root_g = self.$e.selectAll("#root_g")
    if ($root_g[0].length === 0) {
      $root_g = draw_svg(self.$e)
    }

    var xscale = create_xscale(data, xattr)
    var yscale = create_yscale(data, yattr)
    draw_axis(data, xscale, yscale, $root_g)

    var subsystem_names = set(data.map(function(entry) {
      return entry.subsystem
    }))
    var circles_color_scale = custom_color_scale(subsystem_names)
    draw_circles(data, $root_g, xscale, yscale, xattr, yattr, circles_color_scale)

    var avgdata = get_averages(data, "contributors_tr")
    var median_data = {
      name: "median",
      data: avgdata.map(function(entry) {
        return {
          x: entry[xattr],
          y: entry[yattr + "_median"],
        }
      })
    }
    var mean_data = {
      name: "mean",
      data: avgdata.map(function(entry) {
        return {
          x: entry[xattr],
          y: entry[yattr + "_mean"]
        }
      })
    }
    var path_data = [mean_data, median_data]
    var path_color_scale = d3.scale.category10()
      //draw_paths(path_data, $root_g, xscale, yscale, path_color_scale)
      //draw_path_legend(path_data, $root_g, path_color_scale)
  }

  function draw_svg($parent) {
    var $svg = $parent.append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)

    var $root_g = $svg.append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
      .attr("id", "root_g")

    return $root_g
  }

  // Unused
  function draw_subsystem_legend(data, $svg, color_scale) {
    var rect_width = 6
    var rect_height = 4

    var $g = $svg.append('g')
      .attr('transform', 'translate(30, 0)')

    var $g_row = $g.selectAll('gs')
      .data(data)
      .enter().append('g')
      .attr('transform', function(d, idx) {
        return 'translate(' + rect_width + "," + ((rect_height + 5) * idx) + ")"
      })
      .attr('fill', function(d) {
        return color_scale(d)
      })

    $g_row.append('rect').attr('width', rect_width).attr('height', rect_height)

    $g_row.append('text')
      .attr('x', rect_width + 10)
      .attr('y', rect_height)
      .text(function(d) {
        return d.toUpperCase() + d.substr(1, d.length)
      })
      .style('font-size', 10)
  }


  function draw_path_legend(data, $svg, color_scale) {
    //Todo rewrite so that the container isn't removed 
    var rect_width = 60
    var rect_height = 5

    $svg.selectAll('.path-legend-g').remove()
    var $g = $svg.append('g')
      .attr('transform', 'translate(' + (width - 150) + "," + 100 + ")")
      .attr('class', 'path-legend-g')

    var $gs = $g.selectAll('.legends')
      .data(data)

    $gs.enter().append('g')
      .attr('transform', function(d, idx) {
        var x = rect_width
        var y = (rect_height + 10) * idx
        return 'translate(' + x + ',' + y + ')'
      })
      .attr('fill', function(d) {
        return color_scale(d.name)
      })

    $gs.exit()

    $gs.append('rect')
      .attr('width', rect_width)
      .attr('height', rect_height)

    $gs.append('text')
      .attr('x', rect_width + 10)
      .attr('y', rect_height)
      .text(function(d) {
        return d.name[0].toUpperCase() + d.name.substr(1, d.name.length)
      })
      .style('font-weight', 'bold')
  }


  function draw_circles(data, $svg, xscale, yscale, xattr, yattr, color_scale) {
    var $circles = $svg.selectAll(".circle")
      .data(data)

    //Enter
    $circles
      .enter().append("circle")
      .attr('class', 'circle')
      .attr("r", 4)
      .on("mouseover", function(d) {
        tooltip_V.render(d, xattr, yattr)
      })
      .on("mouseout", tooltip_V.hide)

    //Update
    $circles
      .attr("cx", function(d) {
        return xscale(d[xattr])
      })
      .attr("cy", function(d) {
        return yscale(d[yattr])
      })
      .style("fill", function(d) {
        return color_scale(d.subsystem);
      })
      .style("opacity", function(d) {
        return state.show_circles ? 1 : 0
      })

    //Exit
    $circles.exit().remove()

    return $circles
  }


  function draw_paths(data, $svg, xscale, yscale, color_scale) {
    var line = d3.svg.line()
      .x(function(d) {
        return xscale(d.x)
      })
      .y(function(d) {
        return yscale(d.y)
      })

    var $paths = $svg.selectAll('.path')
      .data(data)

    //Enter
    $paths
      .enter().append('path')
      .attr('class', 'path')

    //Update
    $paths
      .attr('d', function(d) {
        return line(d.data)
      })
      .attr('stroke', function(d) {
        return color_scale(d.name)
      })

    //Exit
    $paths.exit().remove()

    return $paths
  }


  function draw_axis(data, xscale, yscale, $svg) {
    var xAxis = d3.svg.axis().scale(xscale).orient("bottom")
    var yAxis = d3.svg.axis().scale(yscale).orient("left")

    $svg.selectAll('.axis').remove()

    var $xAxis = $svg.append("g")
      .attr("class", "axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)

    var $yAxis = $svg.append("g")
      .attr("class", "axis")
      .call(yAxis)

    $xAxis.append("text")
      .attr("class", "label")
      .attr("x", width)
      .attr("y", -6)
      .style("text-anchor", "end")
      .text("Contributors");

    $yAxis.append("text")
      .attr("class", "label")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Defects");
  }

  function create_xscale(data, attr) {
    var min = d3.min(data, create_accessor(attr)) - 0.5
    var max = d3.max(data, create_accessor(attr))
    var xscale = d3.scale.linear()
      .range([0, width])
      .domain([min, max])
    return xscale
  }

  function create_yscale(data, attr) {
    var min = d3.min(data, create_accessor(attr)) - 0.5
    var max = d3.max(data, create_accessor(attr))
    var yscale = d3.scale.linear()
      .range([height, 0])
      .domain([min, max])
    return yscale
  }

  function create_accessor(attr) {
    return function(d) {
      return d[attr]
    }
  }

  return self
}


/* Helper functions */


/**
 * Considering that the json served isn't actually json, but a more specialized form of arrays where the first
 * entry descirbles the keys for the rest of the entries. This function is used to preprocess that data and convert it
 * to standard json.
 * The keys represent the data keywords in the first row.
 */
function data_toJSON(dataarr) {
  var description = dataarr.shift()
  var json_arr = []

  for (var i = 0; i < dataarr.length; i++) {
    var row = dataarr[i]
    var json_row = {}
    row.forEach(function(column_val, index) {
      var keyword = description[index]
      json_row[keyword] = column_val || 0
    })

    var defects_abc = json_row['defects_a'] + json_row['defects_b'] + json_row['defects_c']
    json_row['defects_abc'] = defects_abc
    json_row['defect_density'] = json_row['nloc'] === 0 ? 0 : defects_abc / json_row['nloc']
    json_row['defect_density_complexity'] = json_row['cyclomatic_complexity'] === 0 ? 
              0 : defects_abc / json_row['cyclomatic_complexity']

    json_arr.push(json_row)
  }

  return json_arr
}


function create_url_params(base_url, param_dict) {
  /**
   * Creates url's with query parameters based on the hash passed as `param_dict`.
   * If the values are JSON serializble, it serializes them
   */
  function add_param(url, key, val) {
    var value = val.toJSON ? val.toJSON() : val
    url += key + "=" + value
    return url + "&"
  }

  var url = base_url + "?"
  Object.keys(param_dict).forEach(function(key) {
    // Encode arrays
    if (Array.isArray(param_dict[key])) {
      param_dict[key].forEach(function(array_val) {
        url = add_param(url, key, array_val)
      })
    }
    else {
      url = add_param(url, key, param_dict[key])
    }
  })

  //Remove last &
  url = url.substring(0, url.length - 1)
  console.info("Using url:", url)
  return url
}


function get_averages(data, xattr) {
  var metric_keys = ["defects", "severity_a", "severity_b", "severity_c", "severity_improvement"]
    /*
     * xattr intended structure
     * {0: {keyA: [values], keyB: [values]}, 3: }
     */
  var xattr_dict = {}
  for (var i = 0; i < data.length; i++) {
    var entry = data[i]
      //Dict that stores arrays for all entries at this xattr value
      //{severity_a: [3, 4, 2], severity_b:[3,2,5]}
    var avg_entry = xattr_dict[entry[xattr]]

    if (!avg_entry) {
      avg_entry = (xattr_dict[entry[xattr]] = {})
      Object.keys(entry).forEach(function(key) {
        if (metric_keys.indexOf(key) > -1) {
          //Entry is missing, add key and a new array
          avg_entry[key] = [entry[key]]
        }
      })
    }
    else {
      Object.keys(entry).forEach(function(key) {
        if (metric_keys.indexOf(key) > -1) {
          avg_entry[key].push(entry[key])
        }
      })
    }
  }

  var asArr = Object.keys(xattr_dict).map(function(attr) {
    var entry = xattr_dict[attr]
    entry[xattr] = attr
    Object.keys(entry).forEach(function(key) {
      entry[key + "_median"] = d3.median(entry[key])
      entry[key + "_mean"] = d3.mean(entry[key])
    })
    return entry
  })
    
  return asArr
}


function set(data) {
  assert(Array.isArray(data))
    /* Returns a set of an array (without duplicates) */
  var existing = {}
  data.forEach(function(d) {
    if (existing[d] === undefined) {
      existing[d] = true
    }
  })
  return Object.keys(existing)
}


function custom_color_scale(domain) {
  /**
   * Returns a d3 color scale based on `n` entries
   * Similar to how d3.scale.categoryxx work, but they only sustain xx amount of random colors. This function returns
   * the `domain.length` of colors.
   */
  assert(Array.isArray(domain))
  var hex = ['a', 'b', 'c', 'd', 'e', 'f', 1, 2, 3, 4, 5, 6, 7, 8, 9]
  var colors = []
  while (true) {
    var color = '#'
    for (var j = 0; j < 6; j++) {
      color += hex[Math.floor(Math.random() * hex.length)]
    }
    if (colors.indexOf(color) === -1) {
      colors.push(color)
    }
    if (colors.length === domain.length) {
      break
    }
  }
  return d3.scale.ordinal().range(colors).domain(domain)
}


function assert(bool, msg) {
  var error_msg = "Assertion Error"
  if (msg) {
    if (typeof msg !== 'string') {
      throw new Error("msg passed to `assert` must be of type `string`")
    }
    error_msg += ": " + msg
  }
  if (!bool) {
    throw new Error("Assertion Error")
  }
}



/*
 * Main func
 */

function main() {
  var state = State(new Date(0), new Date(), false)
  var tooltip_V = Tooltip_V()
  ShowLine_V(state)
  ShowCircles_V(state)
  SelectYears_V(state)
  Srcfiles_V(state)
  SeverityBtns_V(state)

  var url = create_url_params('/contributors_defects_data/', {
    srcfiles: state.attrs.srcfiles,
    startdate: new Date(0),
    enddate: state.attrs.enddate,
    severity: state.attrs.severity
  })


  d3.json(url, function(data) {
    data = data_toJSON(data)
    var chart_V = Chart_V(state, tooltip_V, data)
    chart_V.render(data, "contributors_tr", "defects_abc")
  })
}


main()
