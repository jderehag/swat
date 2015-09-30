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
///<reference path="TreemapApp.ts"/>
var TreemapPackage;
(function (TreemapPackage) {
    var DataLoader;
    (function (DataLoader) {
        DataLoader.load_data = function (metric, metrics, first_child) {
            var promise;
            if (metric.name == Models.METRIC_NAMES.changerate) {
                promise = load_changerate(metrics, first_child);
            }
            else if (metric.name == Models.METRIC_NAMES.risk_assessment) {
            }
            else {
                promise = load_db_metric(metric, first_child);
            }
            return promise;
        };
        var load_db_metric = function (metric, component) {
            /**
             * If the child data has been loaded, it returns a resolved deferred
             * Otherwise it loads data and caches it
             */
            if (component.treemap_data[metric.name] !== undefined) {
                return $.Deferred().resolve();
            }
            var metric_deferred = get_deferred('/treemap_data/', component.parent, metric);
            // The children are a deferred...so we have to pass it through a when
            var promise = $.when(metric_deferred);
            promise.then(function (metric_data) {
                var children = component.parent.children;
                //There are probably metrics for each model
                if (metric_data.length == children.length) {
                    for (var i = 0; i < children.length; i++) {
                        var child = children[i];
                        var metric_entry = metric_data[i];
                        assert_ids_match(child.id, metric_entry[1]);
                        child.treemap_data[metric.name] = metric_entry[2] || 0; //In case of db null
                    }
                }
                else {
                    console.log("Local and server ids do not match, attempting to index...");
                    var data_ids = metric_data.map(function (entry) { return entry[1]; });
                    children.forEach(function (child) {
                        var index = data_ids.indexOf(child.id);
                        // The child has data returned
                        if (index > -1) {
                            child.treemap_data[metric.name] = metric_data[index][2] || 0; //In case of db null
                        }
                        else {
                            child.treemap_data[metric.name] = 0;
                        }
                    });
                }
            });
            return promise;
        };
        var load_changerate = function (metrics, component) {
            /**
             * If the dependencies for each metric are already loaded, it returns a resolved
             * deferred.
             * Otherwise it calls load_db_metric() to load new data, cache it, and then aggregates based
             * on that data
             */
            var dependencies = [Models.METRIC_NAMES.added, Models.METRIC_NAMES.changed,
                Models.METRIC_NAMES.deleted];
            var missing_metrics = dependencies
                .filter(function (name) { return component.treemap_data[name] === undefined; })
                .map(function (name) { return metrics.filter(function (metric) { return metric.name == name; })[0]; });
            if (missing_metrics.length == 0) {
                return $.Deferred().resolve();
            }
            var promises = missing_metrics.map(function (metric) { return load_db_metric(metric, component); });
            var promise = $.when.apply($, [component.parent.children].concat(promises));
            promise.then(function (children) {
                children.forEach(function (child) { return aggregate_changerate(child); });
            });
            return promise;
        };
        var aggregate_changerate = function (cmp) {
            var data = cmp.treemap_data;
            data['changerate'] = data['added'] + data['changed'] + data['deleted'];
        };
        var get_deferred = function (url, component, metric) {
            return Requests.$ajax_wrapper(url, $.extend(component.toJSON(), { 'metric': metric.name }));
        };
        var assert_ids_match = function () {
            var ids = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                ids[_i - 0] = arguments[_i];
            }
            var first = ids[0];
            var filtered = ids.filter(function (id) { return id === first; });
            if (ids.length != filtered.length) {
                throw new Error("Server ID and local ID do not match ids: " + ids);
            }
        };
    })(DataLoader = TreemapPackage.DataLoader || (TreemapPackage.DataLoader = {}));
})(TreemapPackage || (TreemapPackage = {}));
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
///<reference path="../models/Components.ts"/>
///<reference path="../models/Metrics.ts"/>
///<reference path="DataLoader.ts"/>
var TreemapPackage;
(function (TreemapPackage) {
    var State = (function (_super) {
        __extends(State, _super);
        function State(cmp, metrics, size_metric, color_metric) {
            var _this = this;
            _super.call(this);
            this.attrs = {};
            this.existing_metrics = metrics;
            this.attrs.current_component = cmp;
            this.attrs.size_metric = size_metric;
            this.attrs.color_metric = color_metric;
            this.on('update', this, function () {
                console.log("Updating State...", _this.attrs.current_component, _this.attrs.size_metric, _this.attrs.color_metric);
            });
            this.update();
        }
        Object.defineProperty(State.prototype, "size_metric", {
            get: function () {
                return this.attrs.size_metric;
            },
            set: function (metric) {
                this.trigger('start_update');
                this.attrs.size_metric = metric;
                this.update();
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(State.prototype, "color_metric", {
            get: function () {
                return this.attrs.color_metric;
            },
            set: function (metric) {
                this.trigger('start_update');
                this.attrs.color_metric = metric;
                this.update();
            },
            enumerable: true,
            configurable: true
        });
        Object.defineProperty(State.prototype, "current_component", {
            get: function () {
                return this.attrs.current_component;
            },
            set: function (cmp) {
                this.trigger('start_update');
                this.attrs.current_component = cmp;
                console.log("State: Setting current component", cmp);
                this.update();
            },
            enumerable: true,
            configurable: true
        });
        State.prototype.update = function () {
            var _this = this;
            var cmp = this.current_component;
            var done_children = $.Deferred();
            // Handle special case of entering a file with effective complexity,
            // which doesn't exist for that level so normal complexity is returned
            // Set it to a silent update using .attrs because we don't need to update twice
            if (cmp.type == 'file') {
                var complexity = this.existing_metrics.filter(function (metric) { return metric.name == 'cyclomatic_complexity'; })[0];
                if (this.size_metric.name == 'effective_complexity') {
                    this.attrs.size_metric = complexity;
                }
                else if (this.color_metric.name == 'effective_complexity') {
                    this.attrs.color_metric = complexity;
                }
            }
            if (cmp.children.length == 0) {
                console.log('State loading children...');
                cmp.load_children().then(function () { return done_children.resolve(); });
            }
            else
                done_children.resolve();
            done_children.then(function () {
                var size_dfd = TreemapPackage.DataLoader.load_data(_this.size_metric, _this.existing_metrics, cmp.children[0]);
                var color_dfd = TreemapPackage.DataLoader.load_data(_this.color_metric, _this.existing_metrics, cmp.children[0]);
                $.when(size_dfd, color_dfd).then(function () {
                    _this.trigger('update', _this, cmp.children);
                });
            });
        };
        return State;
    })(Framework.EventAPI);
    TreemapPackage.State = State;
})(TreemapPackage || (TreemapPackage = {}));
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
///<reference path="../../../lib/mustache/mustache.d.ts"/>
///reference path="../models/Metrics.ts" />
///<reference path="../State.ts" />
var TreemapPackage;
(function (TreemapPackage) {
    var template_select_size = $("#template_select_size").html();
    var template_select_color = $("#template_select_color").html();
    Mustache.parse(template_select_size);
    Mustache.parse(template_select_color);
    /**
     * Represents the `select` elements that allow you to select the size and color metrics for the treemap.
     * This object is created twice in the application, once for size and once for color. The only thing that
     * differentiates them is that they take a different string as input `(size|color)`.
     * @Todo: Refactor into two separate classes. It makes more sense conceptually.
     */
    var SelectView = (function (_super) {
        __extends(SelectView, _super);
        function SelectView(models, state, type) {
            _super.call(this);
            this.$e = $("<div>");
            this.models = models;
            this.state = state;
            this.template = type == 'size' ? template_select_size : template_select_color;
            this.type = type;
            this.state.on('update', this, this.render.bind(this));
            this.$e.on('change', 'select', this.handle_option_change.bind(this));
            this.render();
        }
        SelectView.prototype.render = function () {
            var metric = this.type == 'size' ? this.state.size_metric.name : this.state.color_metric.name;
            this.$e.html(Mustache.render(this.template, { desc_list: this.models }));
            this.$e.find("select").val(metric);
            this.$e.appendTo(".select-boxes");
        };
        SelectView.prototype.handle_option_change = function () {
            var selected_opt = this.$e.find('select').val();
            console.log("Updating metric", selected_opt);
            if (this.type == 'size') {
                this.state.size_metric = this.models.filter(function (metric) { return metric.name == selected_opt; })[0];
            }
            else {
                this.state.color_metric = this.models.filter(function (metric) { return metric.name == selected_opt; })[0];
            }
        };
        return SelectView;
    })(Framework.EventAPI);
    TreemapPackage.SelectView = SelectView;
    /**
     * Represents a bootstrap style breadcrumb that is used for navigation
     * Listens for changes on the state object or the DOM `li` elements it generates and updates accordingly.
     */
    var breadcrumb_template = $("#breadcrumb_template").html();
    Mustache.parse(breadcrumb_template);
    var BreadCrumbView = (function (_super) {
        __extends(BreadCrumbView, _super);
        function BreadCrumbView(state) {
            _super.call(this);
            this.$e = $("#breadcrumb-container");
            this.template = breadcrumb_template;
            this.state = state;
            this.state.on("update", this, this.render.bind(this));
            this.$e.on('click', '.root', this.handle_root_click.bind(this));
            this.$e.on('click', '.subsystem', this.handle_subsystem_click.bind(this));
            this.$e.on('click', '.file', this.handle_file_click.bind(this));
        }
        BreadCrumbView.prototype.handle_root_click = function () {
            var cmp = this.state.current_component;
            if (cmp.type == 'root')
                this.state.current_component = cmp;
            else if (cmp.type == 'subsystem')
                this.state.current_component = cmp.parent;
            else if (cmp.type == 'file')
                this.state.current_component = cmp.parent.parent;
        };
        BreadCrumbView.prototype.handle_subsystem_click = function () {
            var cmp = this.state.current_component;
            if (cmp.type == 'subsystem')
                this.state.current_component = cmp;
            else if (cmp.type == 'file')
                this.state.current_component = cmp.parent;
        };
        BreadCrumbView.prototype.handle_file_click = function () {
            var cmp = this.state.current_component;
            if (cmp.type == 'file')
                this.state.current_component = cmp;
        };
        BreadCrumbView.prototype.render = function () {
            var data = {
                root: undefined,
                subsystem: undefined,
                file: undefined,
            };
            var cmp = this.state.current_component;
            if (cmp.type == 'root') {
                data.root = cmp;
            }
            else if (cmp.type == 'subsystem') {
                data.root = cmp.parent;
                data.subsystem = cmp;
            }
            else if (cmp.type == 'file') {
                data.root = cmp.parent.parent;
                data.subsystem = cmp.parent;
                data.file = cmp;
            }
            this.$e.html(Mustache.render(this.template, data));
        };
        return BreadCrumbView;
    })(Framework.EventAPI);
    TreemapPackage.BreadCrumbView = BreadCrumbView;
    /**
     * Represents the loader that blocks the UI when new data is loading
     * Listens for state update events.
     */
    var LoaderView = (function (_super) {
        __extends(LoaderView, _super);
        function LoaderView(state) {
            var _this = this;
            _super.call(this);
            this.$e = $('#loader');
            this.state = state;
            this.$e.show();
            state.on('start_update', this, function () { return _this.$e.show(); });
            state.on('update', this, function () { return _this.$e.hide(); });
        }
        return LoaderView;
    })(Framework.EventAPI);
    TreemapPackage.LoaderView = LoaderView;
})(TreemapPackage || (TreemapPackage = {}));
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
///<reference path="../../../lib/jquery/jquery.d.ts" />
///<reference path="../../../lib/d3/d3.d.ts" />
///<reference path="../../framework/View.ts" />
///<reference path="../../framework/Event.ts" />
///<reference path="../TreemapApp.ts" />
///<reference path="../State.ts" />
var TreemapPackage;
(function (TreemapPackage) {
    var Treemap = (function (_super) {
        __extends(Treemap, _super);
        function Treemap(state) {
            var _this = this;
            _super.call(this);
            this.$e = $('#treemap');
            this.model = state;
            this.contextmenu_view = new ContextMenuView(state);
            this.model.on('update', this, function (evtname, data) {
                _this.render.apply(_this, data);
            });
            this.$e.on('click', '.d3plus_data', this.handle_click.bind(this));
            this.$e.on('contextmenu', '.d3plus_data', this.handle_contextmenu.bind(this));
        }
        Treemap.prototype.render = function (state, children) {
            var data = this.adapt_data_for_d3(state, children);
            var color_scale = this.create_color_scale(children, state.color_metric.name);
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
                .color(function (d3_cmp) {
                return color_scale(d3_cmp.color_value);
            })
                .format({
                text: function (text) {
                    // Text is the key passed to the object
                    if (text === 'size_value') {
                        return state.size_metric.name;
                    }
                    else if (text === 'color_value') {
                        return state.color_metric.name;
                    }
                    else {
                        return text;
                    }
                },
                number: function (number, key) {
                    if (number < 0.1) {
                        return number;
                    }
                    else {
                        return d3plus.number.format(number, key);
                    }
                }
            })
                .draw();
        };
        Treemap.prototype.handle_click = function (event) {
            var current_cmp = this.model.current_component;
            if (['root', 'subsystem'].indexOf(current_cmp.type) != -1) {
                var id = $(event.target).data('component_id');
                var cmp = current_cmp.children.filter(function (child) { return child.id == id; })[0];
                this.model.current_component = cmp;
            }
        };
        Treemap.prototype.handle_contextmenu = function (event) {
            event.preventDefault();
            var id = $(event.target).data('component_id');
            var cmp = this.model.current_component.children.filter(function (child) { return child.id == id; })[0];
            this.contextmenu_view.last_clicked_cmp = cmp;
            this.contextmenu_view.$e.css({
                // offsetX is not supported in FF...
                left: (event.offsetX || event.pageX - this.$e.offset().left),
                top: (event.offsetY || event.pageY - this.$e.offset().top),
                display: "block"
            });
        };
        Treemap.prototype.adapt_data_for_d3 = function (state, children) {
            var adapted = children.map(function (child) {
                var o = {};
                o["id"] = child.id;
                o["name"] = child.name;
                o["abspath"] = child["abspath"];
                o["size_value"] = child.treemap_data[state.size_metric.name];
                o["color_value"] = child.treemap_data[state.color_metric.name];
                return o;
            });
            return adapted;
        };
        Treemap.prototype.create_color_scale = function (children, color_metric) {
            var max_cmp = children.reduce(function (ch1, ch2) {
                var v1 = ch1.treemap_data[color_metric];
                var v2 = ch2.treemap_data[color_metric];
                return v1 > v2 ? ch1 : ch2;
            });
            var val = max_cmp.treemap_data[color_metric];
            var max;
            if (color_metric == 'effective_complexity') {
                max = 1.0;
            }
            else {
                max = val > 15 ? val : 15;
            }
            return d3.scale.linear().range(['green', 'red']).domain([0, max]);
        };
        return Treemap;
    })(Framework.EventAPI);
    TreemapPackage.Treemap = Treemap;
    var ContextMenuView = (function (_super) {
        __extends(ContextMenuView, _super);
        function ContextMenuView(state) {
            var _this = this;
            _super.call(this);
            this.$e = $('#contextMenu');
            this.state = state;
            this.$e.on('click', '.up-one-level', function () { return _this.handle_up_one_level(); });
            this.$e.on('click', '.view-chart', function () { return _this.handle_view_chart(); });
            this.$e.on('click', '.copy-path', function () { return _this.handle_copy_path(); });
            this.$e.on('click', '.remove', function () { return _this.handle_remove_component(); });
            this.$e.on('click', '.reset', function () { return _this.handle_reset(); });
            $(document).on('click', this.handle_hide.bind(this));
            /* Todo: Fix */
            this.$e.find('.view-chart').hide();
        }
        ContextMenuView.prototype.handle_hide = function (event) {
            if (this.$e.is(':visible')) {
                //If right click
                if (event.which == 1)
                    this.$e.hide();
            }
        };
        ContextMenuView.prototype.handle_up_one_level = function () {
            var grandparent = this.last_clicked_cmp.parent.parent;
            if (grandparent !== undefined) {
                this.state.current_component = grandparent;
            }
        };
        ContextMenuView.prototype.handle_view_chart = function () {
        };
        ContextMenuView.prototype.handle_copy_path = function () {
            var msg;
            if (this.last_clicked_cmp["abspath"])
                msg = "Absolute path: Ctrl+C, Enter";
            else
                msg = "The component has no absolute path";
            window.prompt(msg, this.last_clicked_cmp["abspath"] || "None found");
        };
        ContextMenuView.prototype.handle_remove_component = function () {
            var _this = this;
            var removed_cmp = this.last_clicked_cmp;
            this.state.current_component.children.forEach(function (child, index, children) {
                if (child.id == removed_cmp.id) {
                    children.splice(index, 1);
                    _this.state.update();
                }
            });
        };
        ContextMenuView.prototype.handle_reset = function () {
            // TODO: Reset to cached copy
            var cmp = this.last_clicked_cmp;
            this.state.current_component.children = [];
            this.state.update();
        };
        return ContextMenuView;
    })(Framework.EventAPI);
})(TreemapPackage || (TreemapPackage = {}));
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
///<reference path="../models/Components.ts"/>
///<reference path="../models/Metrics.ts"/>
///<reference path="./views/Widgets.ts" />
///<reference path="./views/Treemap.ts" />
///<reference path="./State.ts" />
///<reference path="../util/Requests.ts" />
var TreemapPackage;
(function (TreemapPackage) {
    var TreemapApp = (function () {
        function TreemapApp(metrics) {
            var defer_metrics_descs = Requests.$ajax_wrapper('/metric_descriptions/');
            $.when(defer_metrics_descs).done(function (descs) {
                var metric_models = descs.map(function (metric) { return new Models.Metric(metric); });
                var nloc_model = metric_models.filter(function (model) { return model.name == 'nloc'; })[0];
                var defect_model = metric_models.filter(function (model) { return model.name == 'defect_modifications'; })[0];
                var state = new TreemapPackage.State(new Models.Root(), metric_models, nloc_model, defect_model);
                var color_select_view = new TreemapPackage.SelectView(metric_models, state, 'color');
                var size_select_view = new TreemapPackage.SelectView(metric_models, state, 'size');
                var breadcrumb = new TreemapPackage.BreadCrumbView(state);
                var loader = new TreemapPackage.LoaderView(state);
                var treemap = new TreemapPackage.Treemap(state);
            });
        }
        return TreemapApp;
    })();
    TreemapPackage.TreemapApp = TreemapApp;
})(TreemapPackage || (TreemapPackage = {}));
//# sourceMappingURL=treemap.bin.js.map