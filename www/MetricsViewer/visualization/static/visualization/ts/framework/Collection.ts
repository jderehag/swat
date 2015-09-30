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

/// <reference path="Event.ts"/>
/// <reference path="Model.ts"/>


module Framework {
  export class Collection<T extends EventAPI> extends EventAPI {
    arr:T[] = []

    constructor(...modelarr:T[]) {
      super()
      if (modelarr) {
        //Set up listeners on models to propagate events to collection
        modelarr.forEach(model => model.on('change', this, this.trigger.bind(this, 'change')))
        this.arr = modelarr
      }

    }

    push(...models:T[]) {
      models.forEach((model) => {
        // Propagate changes to this collection
        model.on('change', this, this.trigger.bind(this, 'change', this.arr, model))
        this.arr.push(model)
      })
      this.trigger('change', this.arr, models)
    }


    remove(predicate :(value: T, index?: number, array?: T[]) => boolean):T  {
      for (var i = 0; i < this.arr.length; i++) {
        if (predicate(this.arr[i])) {
          var elem = this.arr.splice(i, 1)[0]
          elem.off('change', this)
          this.trigger('change', this.arr, elem)
          return elem
        }
      }
    }

    remove_all():void {
      this.arr = []
      this.trigger('change', this.arr)
    }


    find(predicate :(value: T, index?: number, array?: T[]) => boolean) {
      for (var i = 0; i < this.arr.length; i++) {
        if (predicate(this.arr[i], i, this.arr)) {
          return this.arr[i]
        }
      }
    }

    forEach(func: (value: T, index?: number, array?: T[]) => void): void {
      this.arr.forEach(func)
    }

    map(predicate :(value: T, index?: number, array?: T[]) => boolean) {
      return this.arr.map(predicate)
    }

    includes(predicate :(value: T, index?: number, array?: T[]) => boolean) {
      for(var i = 0; i < this.arr.length; i++) {
        if(predicate(this.arr[i], i, this.arr)){
          return true
        }
      }
      return false
    }

  }
}
