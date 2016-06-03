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
import os
from django.conf.urls import url, include

from django.conf import settings

import views
import urls_rest_v0

urlpatterns = [
    # Views that serve html
    url(r'^$', views.treemap_view, name='index'),
    url(r'^treemap/$', views.treemap_view, name='treemapview'),
    url(r'^lineview/$', views.line_view, name='lineview'),
    url(r'^experimental/$', views.experimental_view, name='experimental'),
    url(r'^subsystem_csv_dumper/$', views.subsystem_csv_dumper, name='subsystem_csv_dumper'),
    url(r'^risk_assessment/$', views.risk_assessment_view, name='risk_assessment'),
    url(r'^contributors_defects/$', views.contributors_defects_view, name='contributors_defects'),

    # Views that dump data
    url(r'^get_subsystems/$', views.get_subsystems, name='get_subsystems'),
    url(r'^get_files_for_subsystem/$', views.get_files_for_subsystem, name='get_files_for_subsystem'),
    url(r'^get_functions_for_file/$', views.get_functions_for_file, name='get_functions_for_file'),
    url(r'^metric_descriptions/$', views.metric_descriptions, name='metric_descriptions'),
    url(r'^treemap_data/$', views.treemap_data, name='treemap_data'),
    url(r'^lineview_data/$', views.lineview_data, name='lineview_data'),
    url(r'^contributors_defects_data/$', views.contributors_defects_data, name='contributors_defects_data'),

    # API:s
    url(r'api/v0/', include(urls_rest_v0.urlpatterns))]


# Search through /docs/ and exclicitly add all the URL:s to the URL list.
# We do this to make sure that its impossible to break out of the url sandbox.
# The alternative would be to read the relative path to docs and directly translate it into the physical path
# http://somename/docs/readme.md -> maintainer_scripts/docs/readme.md
# But that opens up the problem with out-of-tree access, for instance one problem could be if you do
# http://somename/docs/../../../etc/passwd
# So instead we statically read all *.md files and creates URL:s to them. That way we can be sure that all paths
# are valid .md files (from docs dir), and that any other request is responded with a 404.
# the downside is that you needs to restart django if you create a new .md file.
# We still read them dynamically though, so any updates inside files can still be done without restarts.
docs_root = 'docs'
urlpatterns += [url(r'^{}$'.format(docs_root + '/'), views.docs_folder, name='docsroot')]
for root, dirs, files in os.walk(settings.REPO_ROOT + os.sep + docs_root):
    for file_ in files:
        if file_.endswith(".md"):
            file_ = os.path.join(root, file_).replace(settings.REPO_ROOT + os.sep, "").replace('\\', '/')
            urlpatterns += [url(r'^(?P<document>{})$'.format(file_), views.docs_markdown)]
    for dir_ in dirs:
        dir_ = os.path.join(root, dir_).replace(settings.REPO_ROOT + os.sep, "").replace('\\', '/') + '/'
        urlpatterns += [url(r'^(?P<dir_>{})$'.format(dir_), views.docs_folder)]


