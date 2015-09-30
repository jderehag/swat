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
import re
from datetime import datetime
from sqlalchemy import func, distinct, and_
from sqlalchemy.orm import aliased
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.http import HttpResponseNotFound
from django.conf import settings
import views_utils

from DbAPI.MetricsDb_ORM import Subsystem, File, Function, ChangeMetric, DefectModification, DefectMeta
from DbAPI.MetricsDb import METRICS
from DbAPI import MetricsDb_TreemapData

'''
Views that serve html files. They can pass values in dictionaries, but for larger datasets
you should dump the data in a separate request instead.
'''
@require_GET
def treemap_view(request):  # pylint: disable=C0111
    return render(request, "visualization/treemap.html")

@require_GET
def line_view(request):  # pylint: disable=C0111
    return render(request, 'visualization/lineview.html')

@require_GET
def experimental_view(request):  # pylint: disable=C0111
    return render(request, "visualization/experimental.html")

@require_GET
def risk_assessment_view(request):  # pylint: disable=C0111
    return render(request, "visualization/risk_assessment.html")

@require_GET
def contributors_defects_view(request):  # pylint: disable=C0111
    return render(request, "visualization/contributors_defects.html")


'''
/docs views
They generally serve things related to /docs, like markdown rendering
'''
@require_GET
def docs_folder(request, dir_='docs'):
    '''
    Searches through dir_ and builds a list of all available .md files
    '''
    md_files = []
    for _, _, files in os.walk(settings.REPO_ROOT + os.sep + dir_):
        for file_ in files:
            if file_.endswith('.md'):
                md_files.append(file_)
        break
    return render(request, "visualization/docs.html", {'breadcrumbs': _breadcrumb_split('/' + dir_),
                                                       'files': md_files})

@require_GET
def docs_markdown(request, document):
    '''
    Takes document and does markdown rendering
    '''
    content = open(settings.REPO_ROOT + os.sep + document, 'r').read()
    return render(request, "visualization/docs.html", {'breadcrumbs': _breadcrumb_split('/' + document),
                                                       'markdown_text': content})


'''
Views that serve standalone data. They should be able to serve both json and csv content.
'''
@require_GET
@views_utils.session_decorator
def get_subsystems(session, request):
    '''
    Returns all subsystems as an array of [subsystem_id, subsystem]
    '''
    response_type = request.GET.get("response_type", "application/json")

    query = session.query(Subsystem.id, Subsystem.subsystem).order_by(Subsystem.id)

    columns = views_utils.get_query_columns(query)
    data = [columns] + query.all()
    return views_utils.dump_data(data, response_type, filename="subsystems")

@require_GET
@views_utils.session_decorator
def get_files_for_subsystem(session, request):
    '''
    Returns all files for a subsystem as an array of [file_id, file]
    '''
    response_type = request.GET.get("response_type", "application/json")
    subsystem_id = request.GET['id']

    query = session.query(File.id, File.file).filter(File.subsystem_id == subsystem_id).order_by(File.id)

    columns = views_utils.get_query_columns(query)
    data = [columns] + query.all()
    return views_utils.dump_data(data, response_type, filename="files")

@require_GET
@views_utils.session_decorator
def get_functions_for_file(session, request):
    '''
    Returns all functions for a file as an array of [function_id, function]
    '''
    response_type = request.GET.get("response_type", "application/json")
    file_id = request.GET['id']

    query = session.query(Function.id, Function.function).filter(Function.file_id == file_id).order_by(Function.id)

    columns = views_utils.get_query_columns(query)
    data = [columns] + query.all()
    return views_utils.dump_data(data, response_type, filename="functions")

@require_GET
def metric_descriptions(_):
    '''
    Todo: Make the output csv compatible
    '''
    # The frontend shifts the first row because it should be agnostic towards both csv and json output
    metrics = ["empty entry for csv"]
    for metric_name, data in METRICS.iteritems():
        entry = {'metric': metric_name}
        entry.update(data)
        metrics.append(entry)

    return views_utils.dump_data(metrics, "application/json")

@require_GET
@views_utils.session_decorator
def treemap_data(session, request):
    '''
    Dumps data that represents the system state at some point in time. Currently it dumps the latest snapshot of the
    system for continuous metrics and data over the past x months for discontinous metrics.

    QueryDict params:
        cmp_type (str):         The type of component for which child data is gathered. E.g if a subsystem is provided,
                                the returned data is all data for the files in that subsystem.
        cmp_id (int):           The component id.
        metric (str):           A metric that must exist in the global METRICS dict.
        response_type (str):    "application/json"|"text/csv"
    '''
    metric = request.GET['metric']
    cmp_type = request.GET['type']
    cmp_id = request.GET.get('id')
    response_type = request.GET.get("response_type", "application/json")

    if metric not in METRICS.keys():
        return HttpResponseNotFound("<h3>Metric not found</h3>")

    query = MetricsDb_TreemapData.get_query(session, metric, cmp_type, cmp_id)
    data = [views_utils.get_query_columns(query)] + query.all()
    return views_utils.dump_data(data, response_type, filename="treemap_data_" + metric)

@require_GET
@views_utils.session_decorator
def lineview_data(session, request):
    '''
    Dumps data that has accumulated over time. This data is best suited for chart like visualizations.

    QueryDict params:
        cmp_type (str):             The type of component. "subsystem"|"file"|"function"
        cmp_id (int):               The component id found in the database
        metric (str):               A metric that must exist in the global METRICS dict.
        response_type (str):        "application/json"|"text/csv"

    Args:
        request (django.http.HttpRequest)

    Returns:
        django.http.HttpResponse
    '''
    cmp_type = request.GET['type']
    cmp_id = request.GET['id']
    metric = request.GET['metric']
    response_type = request.GET.get("response_type", "application/json")

    if metric not in METRICS.keys():
        return HttpResponseNotFound("<h3>Metric not found</h3>")

    db = settings.METRICSDB

    cmp_name = ""
    if cmp_type == "subsystem":
        cmp_name = session.query(Subsystem.subsystem).filter(Subsystem.id == cmp_id).scalar()
        data = db.get_changemetric_for_subsystem(session, cmp_id, metric)

    elif cmp_type == "file":
        cmp_name = session.query(File.file).filter(File.id == cmp_id).scalar()
        data = db.get_changemetric_for_file(session, cmp_id, metric)

    elif cmp_type == "function":
        cmp_name = session.query(Function.function).filter(Function.id == cmp_id).scalar()
        data = db.get_changemetric_for_function(session, cmp_id, metric)

    columns = [["date", "value"]]
    data = columns + views_utils.adapt_data(data)
    return views_utils.dump_data(data, response_type, filename=cmp_name + "_" + metric)

@require_GET
@views_utils.session_decorator
def contributors_defects_data(session, request):
    """
    Returns the contributors and defects for all the files between two dates.

    QueryDict params:
        response_type (str)             'application/json'|'text/csv', default='application/json'
        startdate (json date format)    As per ISO 8601, default=datetime.fromtimestamp(0)
        enddate (json date format)      As per ISO 8601, default=datetime.now()

    Args:
        request (django.http.HttpRequest)

    Returns:
        django.http.HttpResponse
    """
    response_type = request.GET.get("response_type", "application/json")
    startdate = views_utils.str2datetime(request.GET.get('startdate', datetime.fromtimestamp(0).isoformat()))
    enddate = views_utils.str2datetime(request.GET.get('enddate', datetime.now().isoformat()))

    # Pylint incorrectly identifies start/enddate as possible tuples (str2datetime makes sure that is not possible)
    # plus this code is specifically tested in a unittest so its safe.
    filename = "contributors_defects_files_" + startdate.strftime("%Y%m%d") + "-" + enddate.strftime("%Y%m%d")  # pylint: disable=E1101, C0301

    cm1 = aliased(ChangeMetric)
    cm2 = aliased(ChangeMetric)
    cm_metrics = session.query(cm1.file_id,
                               MetricsDb_TreemapData.replace_null_0(func.sum(cm1.nloc)).label("nloc"),
                               MetricsDb_TreemapData.replace_null_0(func.sum(cm1.cyclomatic_complexity))\
                               .label("cyclomatic_complexity"))\
                               .outerjoin(cm2, and_(cm1.function_id == cm2.function_id, cm1.date < cm2.date))\
                               .filter(cm2.date.is_(None))\
                               .group_by(cm1.file_id)\
                               .subquery()

    cm_contributors = session.query(ChangeMetric.file_id,
                                    func.count(distinct(ChangeMetric.user_id)).label('contributors'))\
                                    .filter(ChangeMetric.date.between(startdate, enddate))\
                                    .group_by(ChangeMetric.file_id)\
                                    .subquery()

    defect_mods = session.query(DefectModification.file_id,
                                func.count(distinct(DefectModification.user_id)).label('contributors'),
                                func.count(distinct(DefectModification.defect_id)).label('defects'))\
                                .join(DefectMeta, DefectMeta.id == DefectModification.defect_id)\
                                .filter(DefectModification.date.between(startdate, enddate))\
                                .group_by(DefectModification.file_id)

    defects_a = defect_mods.filter(DefectMeta.severity == 'A').subquery()
    defects_b = defect_mods.filter(DefectMeta.severity == 'B').subquery()
    defects_c = defect_mods.filter(DefectMeta.severity == 'C').subquery()
    defects_improvement = defect_mods.filter(DefectMeta.severity == 'Improvement').subquery()
    defect_mods = defect_mods.subquery()

    # Note, we are only retrieveing files with a subsystem with an inner join
    query = session.query(File.subsystem_id,
                          File.id,
                          File.file,
                          Subsystem.subsystem,
                          MetricsDb_TreemapData.replace_null_0(cm_contributors.c.contributors).label("contributors_cm"),
                          MetricsDb_TreemapData.replace_null_0(defect_mods.c.contributors).label("contributors_tr"),
                          MetricsDb_TreemapData.replace_null_0(defect_mods.c.defects).label("defects"),
                          MetricsDb_TreemapData.replace_null_0(defects_a.c.defects).label("defects_a"),
                          MetricsDb_TreemapData.replace_null_0(defects_b.c.defects).label("defects_b"),
                          MetricsDb_TreemapData.replace_null_0(defects_c.c.defects).label("defects_c"),
                          MetricsDb_TreemapData.replace_null_0(defects_improvement.c.defects)\
                          .label("defects_improvement"),
                          MetricsDb_TreemapData.replace_null_0(cm_metrics.c.cyclomatic_complexity)\
                          .label("cyclomatic_complexity"),
                          MetricsDb_TreemapData.replace_null_0(cm_metrics.c.nloc).label("nloc"))\
                                .join(Subsystem, File.subsystem_id == Subsystem.id)\
                                .outerjoin(cm_metrics, cm_metrics.c.file_id == File.id)\
                                .outerjoin(cm_contributors, cm_contributors.c.file_id == File.id)\
                                .outerjoin(defect_mods, defect_mods.c.file_id == File.id)\
                                .outerjoin(defects_a, defects_a.c.file_id == File.id)\
                                .outerjoin(defects_b, defects_b.c.file_id == File.id)\
                                .outerjoin(defects_c, defects_c.c.file_id == File.id)\
                                .outerjoin(defects_improvement, defects_improvement.c.file_id == File.id)\
                                .order_by(File.id)

    data = [views_utils.get_query_columns(query)] + query.all()
    return views_utils.dump_data(data, response_type, filename=filename)

'''
Common helper functions
'''
def _breadcrumb_split(fullpath):
    paths = [fullpath[:m.start()] for m in re.finditer('/', fullpath)] + [fullpath]
    return [(path, path.split('/')[-1]) for path in paths]
