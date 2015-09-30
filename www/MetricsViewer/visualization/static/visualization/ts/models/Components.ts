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
///<reference path="../../lib/jquery/jquery.d.ts"/>
///<reference path="./JsonI.ts"/>
///<reference path="../util/Requests.ts"/>
module Models {


  export interface treemap_data_type {
    [metric: string]: number
  }


  export interface chart_data_type {
    [metric: string]: [[number, number]]
  }

  /**
   * models used in the app
   */

  export class Base extends Framework.Model {

    constructor(id:number, name:string, type:string, parent:Parent) {
      super({
        id: id,
        name: name,
        type: type,
        parent: parent,
        treemap_data: {},
        chart_data: {}
      })

    }

    get id():number {
      return this.get('id')
    }

    get name():string {
      return this.get('name')
    }

    get parent() {
      return this.get('parent')
    }

    get type():string {
      return this.get('type')
    }

    get treemap_data():treemap_data_type {
      return this.get('treemap_data')
    }

    get chart_data():chart_data_type {
      return this.get('chart_data')
    }

    toJSON() {
      var o = {}
      Object.keys(this.attrs).forEach(key => {
        if(['id', 'name', 'type'].indexOf(key) > -1)
          o[key] = this.attrs[key]
      })
      return o
    }

  }

  export class Parent extends Base{
    get children(): Base[] {
      return this.get('children')
    }
    set children(children: Base[]) {
      this.set('children', children)
    }
    load_children(): JQueryPromise<any> {
      throw new Error("Not implemented")
    }
  }

  export class Root extends Parent{
   constructor() {
     super(0, "root", "root", undefined)
     this.set('children', [])
   }
   j
    get children(): Subsystem[] {
      return this.get('children')
    }
    set children(children: Subsystem[]) {
      this.set('children', children)
    }

    load_children(): JQueryPromise<any> {
      if(this.children.length > 0) {
        console.error("Warning, already loaded children")
        return
      }
      var url = '/get_subsystems/'
      var $deferred = Requests.$ajax_wrapper(url)
      $deferred.then((child_data: [[number, string]]) => {
        this.children = child_data.map(entry => new Subsystem(entry[0], entry[1], this))
      })
      return $deferred
    }

  }

  export class Subsystem extends Parent{
    constructor(id, name, parent:Root) {
      super(id, name, "subsystem", parent)
      this.set('children', [])
    }

    get parent(): Root {
      return this.get('parent')
    }

    get children(): File[] {
      return this.get('children')
    }
    set children(children: File[]) {
      this.set('children', children)
    }

    load_children() : JQueryPromise<any> {
      if(this.children.length > 0) {
        console.error("Warning, already loaded children")
        return
      }
      var url = '/get_files_for_subsystem/'
      var $deferred = Requests.$ajax_wrapper(url , this.toJSON())
      $deferred.then((child_data: [[number, string]]) => {
        this.children = child_data.map(entry => new File(entry[0], entry[1], this))
      })
      return $deferred
    }
  }


  export class File extends Parent{
    constructor(id, name, parent:Subsystem) {
      super(id, name, "file", parent)

      this.set('children', [])
      this.set('abspath', this.name)
      this.set('name', this.abspath.substr(this.abspath.lastIndexOf('/') + 1))
    }

    get parent(): Subsystem {
      return this.get('parent')
    }

    get children(): Func[] {
      return this.get('children')
    }
    set children(children: Func[]) {
      this.set('children', children)
    }

    load_children(): JQueryPromise<any>  {
      if(this.children.length > 0) {
        console.error("Warning, already loaded children")
        return
      }
      var url = '/get_functions_for_file/'
      var $deferred = Requests.$ajax_wrapper(url, this.toJSON())
      $deferred.then((child_data: [[number, string]]) => {
        this.children = child_data.map(entry => new Func(entry[0], entry[1], this))
      })
      return $deferred
    }

    get abspath():string {
      return this.get('abspath')
    }
  }


  var test_empty_name = /^\s*$/
  export class Func extends Base {

    constructor(id, name, parent:File) {
      super(id, name, "function", parent)

      if (test_empty_name.test(this.name)) {
        this.set('name', 'Global Scope')
        this.set('abspath', this.parent.abspath)
      }
    }

    get parent(): File {
      return this.get('parent')
    }

    get abspath():string {
      return this.get('abspath')
    }
  }

  export class TreemapLoader {

  }
}

