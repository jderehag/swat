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

module Framework {
  let global_id = 0

  export interface ev_cache {
    [event_name:string]: {
      [object_id: number]: Function[]
    }
  }

  export class EventAPI {
    /**
     * Every object that inherits from here can be attached to events using `on`,
     * both the callback attaching objects and the event triggering object need unique ids to
     * save the callback in their cache
     */
    __id: number
    event_cache: ev_cache = {}

    constructor() {
      this.__id = ++global_id
    }

    on(ev: string, obj: EventAPI, callback: Function) {
      let ev_entry = this.event_cache[ev] || (this.event_cache[ev] = {})
      let obj_entry: Function[] = ev_entry[obj.__id] || (ev_entry[obj.__id] = [])
      obj_entry.push(callback)
    }

    off(ev: string, obj: EventAPI) {
      this.event_cache[ev][obj.__id] = []
    }

    trigger(ev:string, ...data:any[]) {
      let ev_cache = this.event_cache[ev] || (this.event_cache[ev] = {})
      for(let obj_id of Object.keys(this.event_cache[ev])) {
        this.event_cache[ev][obj_id].forEach(callback => callback.call(this, ev, data))
      }
    }
  }

}
