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

///<reference path="../../../lib/jquery/fancytree/jquery.fancytree.d.ts"/>
///<reference path="../../framework/View.ts"/>
///<reference path="../../framework/Collection.ts"/>
///<reference path="../../models/Components.ts"/>




module LineView {

  /**
   * The view in charge of displaying a hierarchical treeview of components. It is basically a wrapper around Fancytree
   * which implements the actual functionality. We simple manipulate their API here.
   */
  export class TreeView {
    root:RootView
    active_cmps:Framework.Collection<Models.Base>
    $e = $('.tree-panel')
    fancytree:Fancytree.Fancytree

    constructor(root_model: Models.Root, active_cmps: Framework.Collection<Models.Base>) {
      this.active_cmps = active_cmps
      this.root = new RootView(root_model)
      var root_model = this.root.model
      this.bind_events()

      var fancytree_el:any = this.$e.find("#tree").fancytree({
        source: this.root.children,
        extensions: ["filter"],
        filter: {
          mode: "hide",
          autoApply: true
        },
        checkbox: true,
        icons: false,
        select: (event, data) => this.handle_select(event, data),
        lazyLoad: (event, data) => this.handle_lazyload(event, data),
      })

      this.fancytree = fancytree_el.fancytree("getTree")
    }

    bind_events() {
      this.$e.on('keyup', '#tree-search', (event) => this.filter_nodes(event))
    }

    handle_select(event, data) {
      var selected = data.node.selected
      var view:any = data.node.data
      if (selected) this.active_cmps.push(view.model)
      else this.active_cmps.remove(model => model.id == view.model.id)
    }


    /**
     * Note that this function *has to* to assign the child nodes in data.result
     * Nodes that have the property `lazy = true` are called by this method.
     * See `https://github.com/mar10/fancytree/wiki#lazy-loading`
     */
    handle_lazyload(event, data) {
      var lazy_view :any= data.node.data
      var $deferred = lazy_view.model.load_children()
      data.result = $deferred.then(() => {
        lazy_view.create_children(lazy_view.model.children)
        return lazy_view.children
      })
    }

    filter_nodes(event) {
      var text = event.target.value
      if ($.trim(text) === "") {
        this.fancytree.clearFilter()
      }
      else {
        this.fancytree.filterNodes(text)
      }
    }
  }


  /**
   * Basic properties that node objects in Fancytree either must or should have.
   * `key` and `title` are mandatory.
   */
  export interface FancyTreeNode {
    key: number
    title: string

    parent?: any
    children?: any
  }

  /**
   * Base class that implements the FancyTreeNode interface.
   * Each Fancytreenode, whether it's a child or parent *should* extend from this class
   */
  export class BaseNodeView implements FancyTreeNode {
    model:Models.Base
    key:number
    title:string
    data = this

    constructor(model:Models.Base) {
      this.model = model
      this.key = model.id
      this.title = model.name
    }
  }

  /**
   * Actual implementations of the Fancytreenodes
   */
  export class RootView {
    model:Models.Root
    children:SubsystemNodeView[] = []

    constructor(model:Models.Root) {
      this.model = model
      this.children = this.model.children.map(child => new SubsystemNodeView(child, this))
    }
  }

  export class SubsystemNodeView extends BaseNodeView {
    model:Models.Subsystem
    key:number;
    title:string;
    children:FileNodeView[] = []

    //`lazy` indicates that this nodes children are loaded asynchronously through a server call.
    lazy = true

    constructor(model:Models.Subsystem, parent: any) {
      super(model)
    }

    create_children(models :Models.File[]) {
      this.children = models.map(model => new FileNodeView(model, this))
    }
  }

  export class FileNodeView extends BaseNodeView {
    model:Models.File
    parent:any
    children:FuncNodeView[] = []

    lazy = true

    constructor(model:Models.File, parent:any) {
      super(model)
      this.parent = parent
      if(model.children == undefined) {
        console.log("missing", model)
      }
    }
    create_children(models: Models.Func[]) {
      this.children = models.map(model => new FuncNodeView(model, this))
    }
  }

  export class FuncNodeView extends BaseNodeView {
    model:Models.Func
    parent:FileNodeView

    constructor(model:Models.Func, parent:any) {
      super(model)
      this.parent = parent
    }
  }

}
