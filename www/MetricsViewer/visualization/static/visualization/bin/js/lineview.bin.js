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
var Framework;
(function (Framework) {
    var global_id = 0;
    var EventAPI = (function () {
        function EventAPI() {
            this.event_cache = {};
            this.__id = ++global_id;
        }
        EventAPI.prototype.on = function (ev, obj, callback) {
            var ev_entry = this.event_cache[ev] || (this.event_cache[ev] = {});
            var obj_entry = ev_entry[obj.__id] || (ev_entry[obj.__id] = []);
            obj_entry.push(callback);
        };
        EventAPI.prototype.off = function (ev, obj) {
            this.event_cache[ev][obj.__id] = [];
        };
        EventAPI.prototype.trigger = function (ev) {
            var _this = this;
            var data = [];
            for (var _i = 1; _i < arguments.length; _i++) {
                data[_i - 1] = arguments[_i];
            }
            var ev_cache = this.event_cache[ev] || (this.event_cache[ev] = {});
            for (var _a = 0, _b = Object.keys(this.event_cache[ev]); _a < _b.length; _a++) {
                var obj_id = _b[_a];
                this.event_cache[ev][obj_id].forEach(function (callback) { return callback.call(_this, ev, data); });
            }
        };
        return EventAPI;
    })();
    Framework.EventAPI = EventAPI;
})(Framework || (Framework = {}));
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
var __extends = (this && this.__extends) || function (d, b) {
    for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p];
    function __() { this.constructor = d; }
    __.prototype = b.prototype;
    d.prototype = new __();
};
/// <reference path="Event.ts" />
var Framework;
(function (Framework) {
    var Model = (function (_super) {
        __extends(Model, _super);
        function Model(props) {
            _super.call(this);
            this.attrs = {};
            this.previous_attrs = {};
            if (props) {
                this.attrs = props;
            }
        }
        Model.prototype.get = function (key) {
            return this.attrs[key];
        };
        Model.prototype.set = function (key, value) {
            if (!this.attrs[key] !== value) {
                var prev_attrs = this.previous_attrs[key] || (this.previous_attrs[key] = []);
                prev_attrs.push(this.attrs[key]);
                this.attrs[key] = value;
                this.trigger("change", this);
                this.trigger("change:" + key, this);
            }
        };
        Model.prototype.toJSON = function () {
            return this.attrs;
        };
        Model.prototype.toTemplate = function () {
            return this.attrs;
        };
        return Model;
    })(Framework.EventAPI);
    Framework.Model = Model;
})(Framework || (Framework = {}));
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
///<reference path="../../lib/jquery/jquery.d.ts"/>
var Requests;
(function (Requests) {
    Requests.urls = {
        get_subsystems: '/get_subsystems/',
        get_files_for_subsystem: '/get_files_for_subsystem/',
        get_functions_for_file: '/get_functions_for_file/',
        treemap: '/treemap/',
        treemap_data: '/treemap_data/',
        lineview: '/lineview/',
        lineview_data: '/lineview_data/',
        metric_descriptions: '/metric_descriptions/',
        docs: '/docs/'
    };
    //As the event based system may cause things to change quickly via the UI, it may
    //call double initial requests because of missing data. If we instead check for the
    //already active deferreds, and return from this cache we avoid the double request problem.
    var deferred_cache = {};
    Requests.$ajax_wrapper = function (url, query_params, response_type, jqueryopts) {
        if (response_type === void 0) { response_type = "application/json"; }
        /**
         * Wrapper around $.ajax which is used primarily to cache data and preprocess it
         * Note that if the server replies with mimetype json, jquery will automagically parse it!
         * Parsing it twice will cause errors, so specify the json mimetype on server side.
         */
        var options = {
            // jQuery has a bias towards php and has adapted the encoding of data towards php frameworks
            // Use traditional to make it Django compatible.
            traditional: true,
            cache: true,
            //Default vals for the opts
            type: 'GET',
            async: true,
            //query params
            data: {}
        };
        if (query_params)
            Object.keys(query_params).forEach(function (param) { return options.data[param] = query_params[param]; });
        options.data["response_type"] = response_type;
        if (jqueryopts)
            Object.keys(jqueryopts).forEach(function (opt) { return options[opt] = jqueryopts[opt]; });
        //Why serialized with json and not only url? Requests are different depending on the request parametetrs
        var serialized_opts = url + JSON.stringify(options);
        if (deferred_cache[serialized_opts]) {
            console.log("Returning cached deferred");
            return deferred_cache[serialized_opts];
        }
        else {
            console.log("Caching new deferred:", url, "query params:", query_params);
            var deferred = $.when($.ajax(url, options));
            deferred_cache[serialized_opts] = deferred;
            // Shift the first row since we use csv compatible json output. The first row describes the rest
            deferred = deferred.then(function (data) {
                console.info("Server data received for", url, query_params);
                if (data[0][0] !== "string") {
                    new Error("The first row in dumped data should describe the other rows");
                }
                var removed_row = data.shift();
                console.info("Remvoing descriptive row", removed_row);
                return data;
            });
            return deferred;
        }
    };
})(Requests || (Requests = {}));
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
var Models;
(function (Models) {
    /**
     * models used in the app
     */
    var Base = (function (_super) {
        __extends(Base, _super);
        function Base(id, name, type, parent) {
            _super.call(this, {
                id: id,
                name: name,
                type: type,
                parent: parent,
                treemap_data: {},
                chart_data: {}
            });
        }
        Object.defineProperty(Base.prototype, "id", {
            get: function () {
                return this.get('id');
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(Base.prototype, "name", {
            get: function () {
                return this.get('name');
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(Base.prototype, "parent", {
            get: function () {
                return this.get('parent');
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(Base.prototype, "type", {
            get: function () {
                return this.get('type');
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(Base.prototype, "treemap_data", {
            get: function () {
                return this.get('treemap_data');
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(Base.prototype, "chart_data", {
            get: function () {
                return this.get('chart_data');
            },
            enumerable: true,
            configurable: true
        });
        Base.prototype.toJSON = function () {
            var _this = this;
            var o = {};
            Object.keys(this.attrs).forEach(function (key) {
                if (['id', 'name', 'type'].indexOf(key) > -1)
                    o[key] = _this.attrs[key];
            });
            return o;
        };
        return Base;
    })(Framework.Model);
    Models.Base = Base;
    var Parent = (function (_super) {
        __extends(Parent, _super);
        function Parent() {
            _super.apply(this, arguments);
        }
        Object.defineProperty(Parent.prototype, "children", {
            get: function () {
                return this.get('children');
            },
            set: function (children) {
                this.set('children', children);
            },
            enumerable: true,
            configurable: true
        });
        Parent.prototype.load_children = function () {
            throw new Error("Not implemented");
        };
        return Parent;
    })(Base);
    Models.Parent = Parent;
    var Root = (function (_super) {
        __extends(Root, _super);
        function Root() {
            _super.call(this, 0, "root", "root", undefined);
            this.set('children', []);
        }
        Object.defineProperty(Root.prototype, "children", {
            get: function () {
                return this.get('children');
            },
            set: function (children) {
                this.set('children', children);
            },
            enumerable: true,
            configurable: true
        });
        Root.prototype.load_children = function () {
            var _this = this;
            if (this.children.length > 0) {
                console.error("Warning, already loaded children");
                return;
            }
            var url = '/get_subsystems/';
            var $deferred = Requests.$ajax_wrapper(url);
            $deferred.then(function (child_data) {
                _this.children = child_data.map(function (entry) { return new Subsystem(entry[0], entry[1], _this); });
            });
            return $deferred;
        };
        return Root;
    })(Parent);
    Models.Root = Root;
    var Subsystem = (function (_super) {
        __extends(Subsystem, _super);
        function Subsystem(id, name, parent) {
            _super.call(this, id, name, "subsystem", parent);
            this.set('children', []);
        }
        Object.defineProperty(Subsystem.prototype, "parent", {
            get: function () {
                return this.get('parent');
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(Subsystem.prototype, "children", {
            get: function () {
                return this.get('children');
            },
            set: function (children) {
                this.set('children', children);
            },
            enumerable: true,
            configurable: true
        });
        Subsystem.prototype.load_children = function () {
            var _this = this;
            if (this.children.length > 0) {
                console.error("Warning, already loaded children");
                return;
            }
            var url = '/get_files_for_subsystem/';
            var $deferred = Requests.$ajax_wrapper(url, this.toJSON());
            $deferred.then(function (child_data) {
                _this.children = child_data.map(function (entry) { return new File(entry[0], entry[1], _this); });
            });
            return $deferred;
        };
        return Subsystem;
    })(Parent);
    Models.Subsystem = Subsystem;
    var File = (function (_super) {
        __extends(File, _super);
        function File(id, name, parent) {
            _super.call(this, id, name, "file", parent);
            this.set('children', []);
            this.set('abspath', this.name);
            this.set('name', this.abspath.substr(this.abspath.lastIndexOf('/') + 1));
        }
        Object.defineProperty(File.prototype, "parent", {
            get: function () {
                return this.get('parent');
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(File.prototype, "children", {
            get: function () {
                return this.get('children');
            },
            set: function (children) {
                this.set('children', children);
            },
            enumerable: true,
            configurable: true
        });
        File.prototype.load_children = function () {
            var _this = this;
            if (this.children.length > 0) {
                console.error("Warning, already loaded children");
                return;
            }
            var url = '/get_functions_for_file/';
            var $deferred = Requests.$ajax_wrapper(url, this.toJSON());
            $deferred.then(function (child_data) {
                _this.children = child_data.map(function (entry) { return new Func(entry[0], entry[1], _this); });
            });
            return $deferred;
        };
        Object.defineProperty(File.prototype, "abspath", {
            get: function () {
                return this.get('abspath');
            },
            enumerable: true,
            configurable: true
        });
        return File;
    })(Parent);
    Models.File = File;
    var test_empty_name = /^\s*$/;
    var Func = (function (_super) {
        __extends(Func, _super);
        function Func(id, name, parent) {
            _super.call(this, id, name, "function", parent);
            if (test_empty_name.test(this.name)) {
                this.set('name', 'Global Scope');
                this.set('abspath', this.parent.abspath);
            }
        }
        Object.defineProperty(Func.prototype, "parent", {
            get: function () {
                return this.get('parent');
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(Func.prototype, "abspath", {
            get: function () {
                return this.get('abspath');
            },
            enumerable: true,
            configurable: true
        });
        return Func;
    })(Base);
    Models.Func = Func;
    var TreemapLoader = (function () {
        function TreemapLoader() {
        }
        return TreemapLoader;
    })();
    Models.TreemapLoader = TreemapLoader;
})(Models || (Models = {}));
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
var Framework;
(function (Framework) {
    var Collection = (function (_super) {
        __extends(Collection, _super);
        function Collection() {
            var _this = this;
            var modelarr = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                modelarr[_i - 0] = arguments[_i];
            }
            _super.call(this);
            this.arr = [];
            if (modelarr) {
                //Set up listeners on models to propagate events to collection
                modelarr.forEach(function (model) { return model.on('change', _this, _this.trigger.bind(_this, 'change')); });
                this.arr = modelarr;
            }
        }
        Collection.prototype.push = function () {
            var _this = this;
            var models = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                models[_i - 0] = arguments[_i];
            }
            models.forEach(function (model) {
                // Propagate changes to this collection
                model.on('change', _this, _this.trigger.bind(_this, 'change', _this.arr, model));
                _this.arr.push(model);
            });
            this.trigger('change', this.arr, models);
        };
        Collection.prototype.remove = function (predicate) {
            for (var i = 0; i < this.arr.length; i++) {
                if (predicate(this.arr[i])) {
                    var elem = this.arr.splice(i, 1)[0];
                    elem.off('change', this);
                    this.trigger('change', this.arr, elem);
                    return elem;
                }
            }
        };
        Collection.prototype.remove_all = function () {
            this.arr = [];
            this.trigger('change', this.arr);
        };
        Collection.prototype.find = function (predicate) {
            for (var i = 0; i < this.arr.length; i++) {
                if (predicate(this.arr[i], i, this.arr)) {
                    return this.arr[i];
                }
            }
        };
        Collection.prototype.forEach = function (func) {
            this.arr.forEach(func);
        };
        Collection.prototype.map = function (predicate) {
            return this.arr.map(predicate);
        };
        Collection.prototype.includes = function (predicate) {
            for (var i = 0; i < this.arr.length; i++) {
                if (predicate(this.arr[i], i, this.arr)) {
                    return true;
                }
            }
            return false;
        };
        return Collection;
    })(Framework.EventAPI);
    Framework.Collection = Collection;
})(Framework || (Framework = {}));
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
///<reference path="../../lib/jquery/jquery.d.ts"/>
///<reference path="./Event.ts"/>
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
var Models;
(function (Models) {
    var Metric = (function (_super) {
        __extends(Metric, _super);
        function Metric(data) {
            _super.call(this, {
                name: data.metric,
                url: data.url,
                continuous: data.continuous,
            });
        }
        Object.defineProperty(Metric.prototype, "name", {
            /**
             * Database attributes
             */
            get: function () {
                return this.get('name');
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(Metric.prototype, "url", {
            get: function () {
                return this.get('url');
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(Metric.prototype, "continuous", {
            get: function () {
                return this.get('continuous');
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(Metric.prototype, "chart_type", {
            /**
             * Frontend attributes
             */
            get: function () {
                return this.get('chart_type');
            },
            set: function (chart_type) {
                this.set('chart_type', chart_type);
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(Metric.prototype, "histogram_interval", {
            get: function () {
                return this.get('histogram_interval');
            },
            set: function (interval) {
                this.set('histogram_interval', interval);
            },
            enumerable: true,
            configurable: true
        });
        Metric.prototype.toJSON = function () {
            var _this = this;
            var o = {};
            Object.keys(this.attrs).forEach(function (key) {
                if (['name', 'continuous'].indexOf(key) > -1)
                    o[key] = _this.attrs[key];
            });
            return o;
        };
        return Metric;
    })(Framework.Model);
    Models.Metric = Metric;
    /**
     * Ease of access, avoiding misspelling
     */
    Models.METRIC_NAMES = {
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
    };
})(Models || (Models = {}));
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
var LineView;
(function (LineView) {
    var Constants;
    (function (Constants) {
        Constants.CHART_BUTTONS_TIMEOUT = 200;
    })(Constants = LineView.Constants || (LineView.Constants = {}));
})(LineView || (LineView = {}));
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
var LineView;
(function (LineView) {
    var MetricPanelView = (function (_super) {
        __extends(MetricPanelView, _super);
        function MetricPanelView(metrics, active_metrics) {
            var _this = this;
            _super.call(this);
            this.$e = $('.metricpanel-view');
            this.button_views = [];
            metrics.forEach(function (metric) {
                var button_view = new MetricButtonView(metric, active_metrics);
                _this.button_views.push(button_view);
            });
            this.render();
        }
        MetricPanelView.prototype.render = function () {
            var _this = this;
            this.$e.find('.metricrow-container').empty();
            this.button_views.forEach(function (button_view) {
                _this.$e.find('.metricrow-container').append(button_view.$e);
            });
            var defects_btn = this.button_views.filter(function (btn) { return btn.model.name == 'defect_modifications'; })[0];
            var nloc_btn = this.button_views.filter(function (btn) { return btn.model.name == 'nloc'; })[0];
            // Set initially clicked btns
            defects_btn.$e.find('.histogram-button').click();
            nloc_btn.$e.find('.line-button').click();
        };
        return MetricPanelView;
    })(Framework.EventAPI);
    LineView.MetricPanelView = MetricPanelView;
    var button_template = $('#template_metricrow').html();
    var MetricButtonView = (function (_super) {
        __extends(MetricButtonView, _super);
        function MetricButtonView(model, active_metrics) {
            var _this = this;
            _super.call(this);
            this.$e = $('<tr>');
            this.template = button_template;
            this.slider_attrs = {
                min: 1,
                max: 36,
                step: 1,
                value: 3,
                title: function () { return "interval of " + _this.slider_attrs.value + " months"; }
            };
            this.render = function () {
                var el = Mustache.render(_this.template, _this.model.toTemplate());
                _this.$e.html(el);
                _this.$e.find('.slider').attr(_this.slider_attrs).hide();
            };
            this.bind_events = function () {
                // Whenever our model changes, cause this object to change.
                _this.model.on('change', _this, _this.trigger.bind(_this));
                _this.$e.on('click', '.line-button', _this.handle_btn_group.bind(_this, 'line'));
                _this.$e.on('click', '.histogram-button', _this.handle_btn_group.bind(_this, 'histogram'));
                _this.$e.on('click', '.none-button', _this.handle_btn_group.bind(_this, 'none'));
                _this.$e.on('change', '.slider', function () { return _this.handle_slider_change(); });
            };
            this.model = model;
            this.active_metrics = active_metrics;
            this.bind_events();
            this.render();
            this.model.histogram_interval = this.slider_attrs.value;
        }
        /**
         * Method that handles the changes of slider intervals. It assigns the histogram value to the model through a setter
         * which causes the model to update and in turns causes this object to change.
         */
        MetricButtonView.prototype.handle_slider_change = function () {
            var val = this.$e.find('.slider').prop('value');
            this.$e.find('.slider').prop('title', "interval " + val + " months");
            this.model.histogram_interval = parseInt(val);
        };
        MetricButtonView.prototype.handle_btn_group = function (active) {
            var _this = this;
            if (active === 'histogram') {
                this.$e.find('.slider').show(LineView.Constants.CHART_BUTTONS_TIMEOUT);
            }
            else if (active === 'line') {
                this.$e.find('.slider').hide(LineView.Constants.CHART_BUTTONS_TIMEOUT);
            }
            else {
                this.$e.find('.slider').hide(LineView.Constants.CHART_BUTTONS_TIMEOUT);
            }
            if (active === 'line' || active === 'histogram') {
                this.model.chart_type = active;
                if (!this.active_metrics.includes(function (metric) { return metric.name === _this.model.name; })) {
                    this.active_metrics.push(this.model);
                }
            }
            else {
                this.model.attrs.chart_type = 'none';
                this.active_metrics.remove(function (model) { return model.name == _this.model.name; });
            }
        };
        return MetricButtonView;
    })(Framework.EventAPI);
    LineView.MetricButtonView = MetricButtonView;
    var ExportCsvButtonView = (function (_super) {
        __extends(ExportCsvButtonView, _super);
        function ExportCsvButtonView(cmps, metrics) {
            var _this = this;
            _super.call(this);
            this.$e = $('#export_to_csv');
            this.links_modal = new CSVLinksModal(cmps, metrics);
            this.$e.on('click', function (event) {
                event.preventDefault();
                var urls = _this.links_modal.get_urls(cmps, metrics);
                _this.links_modal.show_modal();
            });
        }
        return ExportCsvButtonView;
    })(Framework.EventAPI);
    LineView.ExportCsvButtonView = ExportCsvButtonView;
    var CSVLinksModal = (function (_super) {
        __extends(CSVLinksModal, _super);
        function CSVLinksModal(cmps, metrics) {
            _super.call(this);
            // This container is appended to the bottom of the page with a height of 0
            this.$e = $('<div>');
            this.template = $('#template_links').html();
            this.cmps = cmps;
            this.metrics = metrics;
            this.render();
            $('body').append(this.$e);
        }
        CSVLinksModal.prototype.render = function () {
            var links = this.get_urls(this.cmps, this.metrics);
            this.$e.html(Mustache.render(this.template, { links: links }));
        };
        CSVLinksModal.prototype.show_modal = function () {
            this.render();
            var bootstrap_modal = this.$e.find('.modal');
            bootstrap_modal.modal('show');
        };
        CSVLinksModal.prototype.get_urls = function (cmps, metrics) {
            var urls = [];
            for (var _i = 0, _a = this.cmps.arr; _i < _a.length; _i++) {
                var cmp = _a[_i];
                for (var _b = 0, _c = this.metrics.arr; _b < _c.length; _b++) {
                    var metric = _c[_b];
                    var url_params = {
                        id: cmp.id,
                        type: cmp.type,
                        metric: metric.name,
                        response_type: 'text/csv'
                    };
                    var url_obj = {
                        url: this.create_url('/lineview_data/', url_params),
                        cmp: cmp,
                        metric: metric
                    };
                    urls.push(url_obj);
                }
            }
            return urls;
        };
        CSVLinksModal.prototype.create_url = function (baseurl, keywords) {
            baseurl += "?";
            Object.keys(keywords).forEach(function (key) { return baseurl += key + "=" + keywords[key] + "&"; });
            //Remove last &
            return baseurl.substr(0, baseurl.length - 1);
        };
        return CSVLinksModal;
    })(Framework.EventAPI);
    LineView.CSVLinksModal = CSVLinksModal;
})(LineView || (LineView = {}));
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
var LineView;
(function (LineView) {
    /**
     * The view responsible for updating the chart.
     * It tracks the `active_cmps` and `active_metrics` and calls `render()` whenever they emit change events. Likewise,
     * it emites `"start_update"` and `"end_update"` when it starts and finishes updating.
     */
    var ChartView = (function (_super) {
        __extends(ChartView, _super);
        function ChartView(cmps, metrics) {
            _super.call(this);
            this.$e = $('#chart-container');
            this.events = {
                start_update: 'start_update',
                end_update: 'end_update'
            };
            /**
             * Formats data for the C3 chart in linear diagram style.
             */
            this.format_line_data = function (metric_data) {
                return {
                    // C3 only takes milis
                    dates: metric_data.map(function (entry) { return entry[0] * 1000; }),
                    values: metric_data.map(function (entry) { return entry[1]; })
                };
            };
            /**
             * Formats data for the C3 chart in a barchart or areachart style.
             * This function splits the data up in intervals and accumulates data for all entries between specific intervals where:
             * interval.startdate < data_entry.date < interval.enddate
             * It returns `dates_vals` similar to the line diagram data, but for summarized date periods.
             */
            this.format_histogram_data = function (metric_data, interval) {
                /*
                */
                // In case we have no dates and vals go no further
                var returnobj = {
                    dates: [],
                    values: []
                };
                if (metric_data.length === 0) {
                    return returnobj;
                }
                var create_interval = function (start, end) {
                    return {
                        start: start,
                        end: end,
                        val: 0
                    };
                };
                var sorted_data = metric_data.sort(function (a, b) {
                    return a[0] - b[0];
                });
                var min_date = sorted_data[0][0];
                var max_date = sorted_data[sorted_data.length - 1][0];
                // Intervals in milisecs
                var interval_size = 2629743.83 * interval;
                var no_of_intervals = Math.ceil((max_date - min_date) / interval_size);
                var intervals = [];
                // start - 1 to ensure that the first data_arr entry is included since the interval
                // ensures that the data entry must be between, but not equal to, it's boundries
                var start = min_date - 1;
                for (var i = 0; i < no_of_intervals; i++) {
                    intervals.push(create_interval(start, start + interval_size));
                    start += interval_size;
                }
                // Todo: Optimize if neccesary. It turns out that using traditional for loops
                // instead of forEach significantly improves speed, so we might not need smarter code
                for (var j = 0; j < sorted_data.length; j++) {
                    for (var k = 0; k < intervals.length; k++) {
                        var data_entry = sorted_data[j];
                        var interval_entry = intervals[k];
                        if (interval_entry.start < data_entry[0] && interval_entry.end > data_entry[0]) {
                            interval_entry.val += data_entry[1];
                        }
                    }
                }
                returnobj.dates = intervals.map(function (entry) { return entry.start * 1000; });
                returnobj.values = intervals.map(function (entry) { return entry.val; });
                return returnobj;
            };
            this.active_cmps = cmps;
            this.active_metrics = metrics;
            this.active_cmps.on("change", this, this.render.bind(this));
            this.active_metrics.on("change", this, this.render.bind(this));
            this.c3chart = c3.generate(this.gen_c3_opts());
            this.render();
        }
        ChartView.prototype.render = function () {
            var _this = this;
            this.trigger(this.events.start_update);
            if (this.active_cmps.arr.length == 0 && this.active_metrics.arr.length == 0) {
                setTimeout(function () {
                    _this.trigger(_this.events.end_update);
                    _this.c3chart.unload();
                }, LineView.Constants.CHART_BUTTONS_TIMEOUT);
            }
            else {
                var deferreds = [];
                this.active_cmps.forEach(function (cmp) {
                    _this.active_metrics.arr.forEach(function (metric) {
                        if (cmp.chart_data[metric.name] === undefined) {
                            console.log("[ChartView]Missing chart data, loading from server", cmp.name, metric.name);
                            var def = Requests.$ajax_wrapper('/lineview_data/', {
                                id: cmp.id,
                                type: cmp.type,
                                metric: metric.name
                            });
                            def.then(function (chart_data) {
                                cmp.chart_data[metric.name] = chart_data;
                            });
                            deferreds.push(def);
                        }
                    });
                });
                $.when.apply($, deferreds).then(function () {
                    var data = _this.format_c3_data(_this.active_cmps.arr, _this.active_metrics.arr);
                    setTimeout(function () {
                        _this.c3chart = c3.generate(data);
                        _this.trigger(_this.events.end_update);
                    }, LineView.Constants.CHART_BUTTONS_TIMEOUT);
                });
            }
        };
        ChartView.prototype.format_c3_data = function (cmps, metrics) {
            var _this = this;
            var opts = this.gen_c3_opts();
            var metric_names = metrics.map(function (metric) { return metric.name; });
            if (metric_names.indexOf("defect_modifications") > -1 && metric_names.length >= 2) {
                opts.axis.y2.show = true;
            }
            cmps.forEach(function (cmp) {
                metrics.forEach(function (metric) {
                    var interval = metric.histogram_interval;
                    var line_name = cmp.name + " - " + metric.name;
                    var ddd; // It's actually [dates_vals] but TSS tools use old compiler so type messes up
                    if (metric.chart_type == 'line') {
                        ddd = _this.format_line_data(cmp.chart_data[metric.name]);
                    }
                    else {
                        ddd = _this.format_histogram_data(cmp.chart_data[metric.name], interval);
                    }
                    var xvals = [line_name + "-x"].concat(ddd.dates);
                    var yvals = [line_name].concat(ddd.values);
                    opts.data.columns.push(xvals, yvals);
                    opts.data.xs[line_name] = line_name + "-x";
                    //If we have defect_modifications and at least [defect_modifications + other metric] 
                    //use defect_modifications on the right axis
                    if (metric.name == 'defect_modifications' && opts.axis.y2.show) {
                        opts.data.axes[line_name] = 'y2';
                    }
                    else {
                        opts.data.axes[line_name] = 'y';
                    }
                    if (metric.chart_type == 'line') {
                        opts.data.types[line_name] = 'line';
                    }
                    else {
                        opts.data.types[line_name] = 'area-step';
                    }
                });
            });
            console.log("opts", opts);
            return opts;
        };
        /**
         * Generates C3 API options. It returns an object that conforms to the C3 API.
         * See `http://c3js.org/reference.html`
         */
        ChartView.prototype.gen_c3_opts = function () {
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
            };
        };
        return ChartView;
    })(Framework.EventAPI);
    LineView.ChartView = ChartView;
    /**
     * A loader object which is show while the chart is in updating state.
     * Once the chart leaves the updating state the loader is hidden.
     */
    var LoaderView = (function (_super) {
        __extends(LoaderView, _super);
        function LoaderView(chartview) {
            var _this = this;
            _super.call(this);
            this.$e = $('#loader');
            this.chartview = chartview;
            this.chartview.on(this.chartview.events.start_update, this, function () { return _this.$e.show(); });
            this.chartview.on(this.chartview.events.end_update, this, function () { return _this.$e.hide(); });
        }
        return LoaderView;
    })(Framework.EventAPI);
    LineView.LoaderView = LoaderView;
})(LineView || (LineView = {}));
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
var LineView;
(function (LineView) {
    /**
     * The view in charge of displaying a hierarchical treeview of components. It is basically a wrapper around Fancytree
     * which implements the actual functionality. We simple manipulate their API here.
     */
    var TreeView = (function () {
        function TreeView(root_model, active_cmps) {
            var _this = this;
            this.$e = $('.tree-panel');
            this.active_cmps = active_cmps;
            this.root = new RootView(root_model);
            var root_model = this.root.model;
            this.bind_events();
            var fancytree_el = this.$e.find("#tree").fancytree({
                source: this.root.children,
                extensions: ["filter"],
                filter: {
                    mode: "hide",
                    autoApply: true
                },
                checkbox: true,
                icons: false,
                select: function (event, data) { return _this.handle_select(event, data); },
                lazyLoad: function (event, data) { return _this.handle_lazyload(event, data); },
            });
            this.fancytree = fancytree_el.fancytree("getTree");
        }
        TreeView.prototype.bind_events = function () {
            var _this = this;
            this.$e.on('keyup', '#tree-search', function (event) { return _this.filter_nodes(event); });
        };
        TreeView.prototype.handle_select = function (event, data) {
            var selected = data.node.selected;
            var view = data.node.data;
            if (selected)
                this.active_cmps.push(view.model);
            else
                this.active_cmps.remove(function (model) { return model.id == view.model.id; });
        };
        /**
         * Note that this function *has to* to assign the child nodes in data.result
         * Nodes that have the property `lazy = true` are called by this method.
         * See `https://github.com/mar10/fancytree/wiki#lazy-loading`
         */
        TreeView.prototype.handle_lazyload = function (event, data) {
            var lazy_view = data.node.data;
            var $deferred = lazy_view.model.load_children();
            data.result = $deferred.then(function () {
                lazy_view.create_children(lazy_view.model.children);
                return lazy_view.children;
            });
        };
        TreeView.prototype.filter_nodes = function (event) {
            var text = event.target.value;
            if ($.trim(text) === "") {
                this.fancytree.clearFilter();
            }
            else {
                this.fancytree.filterNodes(text);
            }
        };
        return TreeView;
    })();
    LineView.TreeView = TreeView;
    /**
     * Base class that implements the FancyTreeNode interface.
     * Each Fancytreenode, whether it's a child or parent *should* extend from this class
     */
    var BaseNodeView = (function () {
        function BaseNodeView(model) {
            this.data = this;
            this.model = model;
            this.key = model.id;
            this.title = model.name;
        }
        return BaseNodeView;
    })();
    LineView.BaseNodeView = BaseNodeView;
    /**
     * Actual implementations of the Fancytreenodes
     */
    var RootView = (function () {
        function RootView(model) {
            var _this = this;
            this.children = [];
            this.model = model;
            this.children = this.model.children.map(function (child) { return new SubsystemNodeView(child, _this); });
        }
        return RootView;
    })();
    LineView.RootView = RootView;
    var SubsystemNodeView = (function (_super) {
        __extends(SubsystemNodeView, _super);
        function SubsystemNodeView(model, parent) {
            _super.call(this, model);
            this.children = [];
            //`lazy` indicates that this nodes children are loaded asynchronously through a server call.
            this.lazy = true;
        }
        SubsystemNodeView.prototype.create_children = function (models) {
            var _this = this;
            this.children = models.map(function (model) { return new FileNodeView(model, _this); });
        };
        return SubsystemNodeView;
    })(BaseNodeView);
    LineView.SubsystemNodeView = SubsystemNodeView;
    var FileNodeView = (function (_super) {
        __extends(FileNodeView, _super);
        function FileNodeView(model, parent) {
            _super.call(this, model);
            this.children = [];
            this.lazy = true;
            this.parent = parent;
            if (model.children == undefined) {
                console.log("missing", model);
            }
        }
        FileNodeView.prototype.create_children = function (models) {
            var _this = this;
            this.children = models.map(function (model) { return new FuncNodeView(model, _this); });
        };
        return FileNodeView;
    })(BaseNodeView);
    LineView.FileNodeView = FileNodeView;
    var FuncNodeView = (function (_super) {
        __extends(FuncNodeView, _super);
        function FuncNodeView(model, parent) {
            _super.call(this, model);
            this.parent = parent;
        }
        return FuncNodeView;
    })(BaseNodeView);
    LineView.FuncNodeView = FuncNodeView;
})(LineView || (LineView = {}));
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
///<reference path="../models/Components.ts"/>
///<reference path="views/ChartView.ts"/>
///<reference path="views/MetricButtonViews.ts"/>
///<reference path="views/TreeView.ts"/>
///<reference path="../framework/Model.ts"/>
///<reference path="../util/Requests.ts"/>
///<reference path="../../lib/jquery/fancytree/jquery.fancytree.d.ts"/>
var LineView;
(function (LineView) {
    var App = (function () {
        function App() {
            var _this = this;
            this.root_model = new Models.Root();
            this.active_cmps = new Framework.Collection();
            this.active_metrics = new Framework.Collection();
            var defer_subsystems = Requests.$ajax_wrapper('/get_subsystems/');
            var defer_metric_descs = Requests.$ajax_wrapper('/metric_descriptions/');
            $.when(defer_subsystems, defer_metric_descs).done(function (subsystem_result, metrics_result) {
                var subsystem_models = subsystem_result.map(function (json) {
                    return new Models.Subsystem(json[0], json[1], _this.root_model);
                });
                //These metrics cant be used in the lineview yet!
                var lineview_incompatible_metrics = ["effective_complexity", "revisions", "defect_density"];
                var metric_models = metrics_result
                    .map(function (metric) { return new Models.Metric(metric); })
                    .filter(function (model) { return lineview_incompatible_metrics.indexOf(model.name) === -1; });
                _this.root_model.children = subsystem_models;
                var metricpanelview = new LineView.MetricPanelView(metric_models, _this.active_metrics);
                var treeview = new LineView.TreeView(_this.root_model, _this.active_cmps);
                var chartview = new LineView.ChartView(_this.active_cmps, _this.active_metrics);
                var exportCsvButton = new LineView.ExportCsvButtonView(_this.active_cmps, _this.active_metrics);
                var loader = new LineView.LoaderView(chartview);
            });
        }
        return App;
    })();
    LineView.App = App;
})(LineView || (LineView = {}));
//# sourceMappingURL=lineview.bin.js.map