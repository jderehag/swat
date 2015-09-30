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

module Models {
  export class Metric extends Framework.Model {
    constructor(data:any) {
      super({
        name: data.metric,
        url: data.url,
        continuous: data.continuous,
      })
    }

    /**
     * Database attributes
     */
    get name():string {
      return this.get('name')
    }

    get url():string {
      return this.get('url')
    }

    get continuous():boolean {
      return this.get('continuous')
    }

    /**
     * Frontend attributes
     */

    get chart_type():string {
      return this.get('chart_type')
    }

    set chart_type(chart_type: string) {
      this.set('chart_type', chart_type)
    }

    get histogram_interval() {
      return this.get('histogram_interval')
    }

    set histogram_interval(interval: number) {
      this.set('histogram_interval', interval)
    }

    toJSON() {
      var o = {}
      Object.keys(this.attrs).forEach(key => {
        if(['name', 'continuous'].indexOf(key) > -1)
          o[key] = this.attrs[key]
      })
      return o
    }
  }

  /**
   * Ease of access, avoiding misspelling
   */
  export var METRIC_NAMES = {
    added: "added",
    changed: "changed",
    deleted: "deleted",
    changerate: "changerate",
    nloc: "nloc",
    token_count: "token_count",
    parameter_count: "parameter_count",
    cyclomatic_complexity: "cyclomatic_complexity",
    effective_complexity: "effective_complexity",
    no_of_revisions: "no_of_revisions",
    risk_assessment: "risk_assessment"
  }
}

