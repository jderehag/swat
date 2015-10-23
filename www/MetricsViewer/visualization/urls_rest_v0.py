'''
Copyright (c) 2015, Jesper Derehag <jesper.derehag@ericsson.com> for Ericsson AB
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

Short description:
'''
from django.conf.urls import url, include

import views_rest_v0
import views_meta_v0

format_re = r'\.(?P<formating>.+)$'
change_rate_re = r'^change_metrics' + format_re
defect_re = r'^defects' + format_re

urlpatterns = []

'''
Subsystems
It is very important that the order for url matching goes in reverse order
i.e start with longest match, and then go inwards.
subsystems/{id}/change_rates.json
subsystems/change_rates.json
subsystems.json
'''
subsystem_kpis = url(r'^meta/', include([url(r'^nloc_threshold' + format_re,
                                             views_meta_v0.subsystem_id_nloc_threshold),
                                         url(r'^cyclomatic_complexity_threshold' + format_re,
                                             views_meta_v0.subsystem_id_complexity_threshold)]))
urlpatterns += [url(r'^subsystems/',
                    include([url(r'^(?P<subsystem_id>\d+)/',
                                 include([url(change_rate_re, views_rest_v0.subsystem_id_change_metrics),
                                          url(r'^function_change_metrics' + format_re,
                                              views_rest_v0.subsystem_id_function_change_metrics),
                                          url(defect_re, views_rest_v0.subsystem_id_defects),
                                          subsystem_kpis])),
                             url(change_rate_re, views_rest_v0.subsystems_change_metrics),
                             url(defect_re, views_rest_v0.subsystems_defects)])),
                url(r'^subsystems' + format_re, views_rest_v0.subsystems)]

'''
Files
It is very important that the order for url matching goes in reverse order
i.e start with longest match, and then go inwards.
files/{id}/change_rates.json
files/change_rates.json
files.json
'''
urlpatterns += [url(r'^files/',
                    include([url(r'^(?P<file_id>\d+)/',
                                 include([url(change_rate_re, views_rest_v0.file_id_change_metrics),
                                          url(defect_re, views_rest_v0.file_id_defects)])),
                             url(change_rate_re, views_rest_v0.files_change_metrics),
                             url(defect_re, views_rest_v0.files_defects)])),
                url(r'^files' + format_re, views_rest_v0.files)]

'''
Functions
It is very important that the order for url matching goes in reverse order
i.e start with longest match, and then go inwards.
functions/{id}/change_rates.json
functions/change_rates.json
functions.json
'''
urlpatterns += [url(r'^functions/',
                    include([url(r'^(?P<function_id>\d+)/',
                                 include([url(change_rate_re, views_rest_v0.function_id_change_metrics),
                                          url(defect_re, views_rest_v0.function_id_defects)])),
                             url(change_rate_re, views_rest_v0.function_change_metrics),
                             url(defect_re, views_rest_v0.function_defects)])),
                url(r'^functions' + format_re, views_rest_v0.functions)]

