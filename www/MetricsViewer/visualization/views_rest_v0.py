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
import array
import datetime
from sqlalchemy import func, and_, distinct

from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_GET

import views_utils

from DbAPI.MetricsDb_ORM import Subsystem, File, Function, ChangeMetric, DefectModification
from DbAPI import MetricsDb
from DbAPI.MetricsDb_TreemapData import replace_null_0


@require_GET
@views_utils.session_decorator
def subsystems(session, _, formating='json'):
    '''
    Returns an array of all subsystems and subsystem_id:s
    See docs/frontends/django_implementation.md for a more detailed description of the format

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
        formating(str):    Indicates wich format that should be returned, [json|csv]
    '''
    query = session.query(Subsystem.id, Subsystem.subsystem).order_by(Subsystem.subsystem)
    return views_utils.dump_data([views_utils.get_query_columns(query)] + query.all(),
                                 response_type=formating, filename=subsystems.__name__)

@require_GET
@views_utils.session_decorator
def subsystems_change_metrics(session, request, formating='json'):
    '''
    Returns an array of change_metrics for all subsystems

    See docs/frontends/django_implementation.md for a more detailed description of the format

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
        formating(str):    Indicates wich format that should be returned, [json|csv]
    '''
    all_fields = ['subsystem_id',
                  'date',
                  'added',
                  'changed',
                  'deleted',
                  'nloc',
                  'token_count',
                  'parameter_count',
                  'cyclomatic_complexity']
    try:
        params = _parse_parameters(all_fields, request)
    except ValueError:
        return HttpResponseBadRequest()

    bins = params['bins']
    if bins is None:
        fid_cache, total_values = _get_initial_continous_data(session, params)

        query = session.query(ChangeMetric.function_id).filter(ChangeMetric.date.between(params['from'], params['to']))\
                                                       .order_by(ChangeMetric.date)
        if 'subsystem_id' in params['fields']:
            query = query.add_columns(File.subsystem_id)
            query = query.filter(File.id == ChangeMetric.file_id)

        total_data = _get_running_totals(query, params['fields'], fid_cache, total_values, [params['fields']])

    elif bins > 0:
        return HttpResponseBadRequest("Not supported yet")

    elif bins == 0:
        query = session.query(File.subsystem_id).outerjoin(ChangeMetric, File.id == ChangeMetric.file_id)\
                                                .group_by(File.subsystem_id)
        total_data = [params['fields']] + _get_change_metric_snapshot(session, params, query)

    return views_utils.dump_data(total_data, response_type=formating, filename=subsystems_change_metrics.__name__)

@require_GET
@views_utils.session_decorator
def subsystems_defects(session, request, formating='json'):
    '''
    Returns an array of defects for all subsystems

    See docs/frontends/django_implementation.md for a more detailed description of the format

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
        formating(str):    Indicates wich format that should be returned, [json|csv]
    '''
    all_fields = ['subsystem_id',
                  'date',
                  'defect_id']
    try:
        params = _parse_parameters(all_fields, request)
    except ValueError:
        return HttpResponseBadRequest()

    query = _add_defect_query_columns(session, params)
    query = query.filter(DefectModification.date.between(params['from'],
                                                         params['to'])).order_by(DefectModification.date)

    if params['bins'] is not None:
        query = query.outerjoin(ChangeMetric, File.id == ChangeMetric.file_id).group_by(File.subsystem_id)

    return views_utils.dump_data([params['fields']] + query.all(),
                                 response_type=formating,
                                 filename=subsystems_defects.__name__)

@require_GET
@views_utils.session_decorator
def subsystem_id_change_metrics(session, request, subsystem_id, formating='json'):
    '''
    Returns an array of change_metrics for a specific subsystem

    See docs/frontends/django_implementation.md for a more detailed description of the format

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
        subsystem_id(int):         : The subsystem_id to be requested
        formating(str):    Indicates wich format that should be returned, [json|csv]
    '''
    all_fields = ['date',
                  'added',
                  'changed',
                  'deleted',
                  'nloc',
                  'token_count',
                  'parameter_count',
                  'cyclomatic_complexity']
    try:
        params = _parse_parameters(all_fields, request)
    except ValueError:
        return HttpResponseBadRequest()

    bins = params['bins']
    if bins is None:
        fid_cache, total_values = _get_initial_continous_data(session, params)

        query = session.query(ChangeMetric.function_id).filter(File.id == ChangeMetric.file_id)\
                                                       .filter(File.subsystem_id == int(subsystem_id))\
                                                       .filter(ChangeMetric.date.between(params['from'], params['to']))\
                                                       .order_by(ChangeMetric.date)

        total_data = _get_running_totals(query, params['fields'], fid_cache, total_values, [params['fields']])

    elif bins > 0:
        return HttpResponseBadRequest("Not supported yet")

    elif bins == 0:
        query = session.query(File.subsystem_id).outerjoin(ChangeMetric, File.id == ChangeMetric.file_id)\
                                                .filter(File.subsystem_id == int(subsystem_id))\
                                                .group_by(File.subsystem_id)
        total_data = [params['fields']] + _get_change_metric_snapshot(session, params, query)

    return views_utils.dump_data(total_data, response_type=formating, filename=subsystem_id_change_metrics.__name__)

@require_GET
@views_utils.session_decorator
def subsystem_id_defects(session, request, subsystem_id, formating='json'):
    '''
    Returns an array of defects for a specific subsystem

    See docs/frontends/django_implementation.md for a more detailed description of the format

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
        subsystem_id(int):         : The subsystem_id to be requested
        formating(str):    Indicates wich format that should be returned, [json|csv]
    '''
    all_fields = ['date',
                  'defect_id']
    try:
        params = _parse_parameters(all_fields, request)
    except ValueError:
        return HttpResponseBadRequest()

    query = _add_defect_query_columns(session, params)
    query = query.filter(DefectModification.date.between(params['from'], params['to']))\
                 .filter(File.id == DefectModification.file_id)\
                 .filter(File.subsystem_id == int(subsystem_id))\
                 .order_by(DefectModification.date)

    if params['bins'] is None:
        query = query.group_by(DefectModification.defect_id)

    return views_utils.dump_data([params['fields']] + query.all(),
                                 response_type=formating,
                                 filename=subsystem_id_defects.__name__)


@require_GET
@views_utils.session_decorator
def files(session, _, formating='json'):
    '''
    Returns an array of all files and file_id:s
    See docs/frontends/django_implementation.md for a more detailed description of the format

    Args:
        session(sqlalchemy session): session to use for queries
        formating(str):    Indicates wich format that should be returned, [json|csv]
    '''
    query = session.query(File.subsystem_id, File.id, File.file).order_by(File.file)
    return views_utils.dump_data([views_utils.get_query_columns(query)] + query.all(),
                                 response_type=formating, filename=files.__name__)

@require_GET
@views_utils.session_decorator
def files_change_metrics(session, request, formating='json'):
    '''
    Returns an array of change_metrics for all files

    See docs/frontends/django_implementation.md for a more detailed description of the format

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
        formating(str):    Indicates wich format that should be returned, [json|csv]
    '''
    all_fields = ['file_id',
                  'date',
                  'added',
                  'changed',
                  'deleted',
                  'nloc',
                  'token_count',
                  'parameter_count',
                  'cyclomatic_complexity']
    try:
        params = _parse_parameters(all_fields, request)
    except ValueError:
        return HttpResponseBadRequest()

    bins = params['bins']
    if bins is None:
        fid_cache, total_values = _get_initial_continous_data(session, params)

        query = session.query(ChangeMetric.function_id).filter(ChangeMetric.date.between(params['from'], params['to']))\
                                                       .order_by(ChangeMetric.date)

        total_data = _get_running_totals(query, params['fields'], fid_cache, total_values, [params['fields']])

    elif bins > 0:
        return HttpResponseBadRequest("Not supported yet")

    elif bins == 0:
        query = session.query(ChangeMetric.file_id).group_by(ChangeMetric.file_id)
        total_data = [params['fields']] + _get_change_metric_snapshot(session, params, query)

    return views_utils.dump_data(total_data, response_type=formating, filename=files_change_metrics.__name__)

@require_GET
@views_utils.session_decorator
def files_defects(session, request, formating='json'):
    '''
    Returns an array of defects for all files

    See docs/frontends/django_implementation.md for a more detailed description of the format

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
        formating(str):    Indicates wich format that should be returned, [json|csv]
    '''
    all_fields = ['file_id',
                  'date',
                  'defect_id']
    try:
        params = _parse_parameters(all_fields, request)
    except ValueError:
        return HttpResponseBadRequest()

    query = _add_defect_query_columns(session, params).filter(DefectModification.date.between(params['from'],
                                                                                              params['to']))\
                                                      .order_by(DefectModification.date)

    if params['bins'] is not None:
        query = query.group_by(DefectModification.file_id)

    return views_utils.dump_data([params['fields']] + query.all(),
                                 response_type=formating,
                                 filename=files_defects.__name__)

@require_GET
@views_utils.session_decorator
def file_id_change_metrics(session, request, file_id, formating='json'):
    '''
    Returns an array of change_metrics for a specific file

    See docs/frontends/django_implementation.md for a more detailed description of the format

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
        file_id(int):         : The file_id to be requested
        formating(str):    Indicates wich format that should be returned, [json|csv]
    '''
    all_fields = ['date',
                  'added',
                  'changed',
                  'deleted',
                  'nloc',
                  'token_count',
                  'parameter_count',
                  'cyclomatic_complexity']
    try:
        params = _parse_parameters(all_fields, request)
    except ValueError:
        return HttpResponseBadRequest()

    bins = params['bins']
    if bins is None:
        fid_cache, total_values = _get_initial_continous_data(session, params)

        query = session.query(ChangeMetric.function_id).filter(ChangeMetric.file_id == int(file_id))\
                                                       .filter(ChangeMetric.date.between(params['from'], params['to']))\
                                                       .order_by(ChangeMetric.date)

        total_data = _get_running_totals(query, params['fields'], fid_cache, total_values, [params['fields']])

    elif bins > 0:
        return HttpResponseBadRequest("Not supported yet")

    elif bins == 0:
        query = session.query(ChangeMetric.file_id).filter(ChangeMetric.file_id == int(file_id))
        total_data = [params['fields']] + _get_change_metric_snapshot(session, params, query)
    return views_utils.dump_data(total_data, response_type=formating, filename=file_id_change_metrics.__name__)

@require_GET
@views_utils.session_decorator
def file_id_defects(session, request, file_id, formating='json'):
    '''
    Returns an array of defects for a specific file

    See docs/frontends/django_implementation.md for a more detailed description of the format

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
        file_id(int):         : The file_id to be requested
        formating(str):    Indicates wich format that should be returned, [json|csv]
    '''

    all_fields = ['date',
                  'defect_id']
    try:
        params = _parse_parameters(all_fields, request)
    except ValueError:
        return HttpResponseBadRequest()

    query = _add_defect_query_columns(session, params)

    query = query.filter(DefectModification.date.between(params['from'], params['to']))\
                 .filter(DefectModification.file_id == int(file_id))\
                 .order_by(DefectModification.date)

    if params['bins'] is None:
        query = query.group_by(DefectModification.defect_id)

    return views_utils.dump_data([params['fields']] + query.all(),
                                 response_type=formating,
                                 filename=file_id_defects.__name__)

@require_GET
@views_utils.session_decorator
def functions(session, _, formating='json'):
    '''
    Returns an array of functions and function_id:s

    See docs/frontends/django_implementation.md for a more detailed description of the format

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
        formating(str):    Indicates wich format that should be returned, [json|csv]
    '''
    query = session.query(Function.file_id, Function.id, Function.function).order_by(Function.function)
    return views_utils.dump_data([views_utils.get_query_columns(query)] + query.all(),
                                 response_type=formating, filename=functions.__name__)

@require_GET
@views_utils.session_decorator
def function_change_metrics(session, request, formating='json'):
    '''
    Returns an array of change_metrics for all functions

    See docs/frontends/django_implementation.md for a more detailed description of the format

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
        formating(str):    Indicates wich format that should be returned, [json|csv]
    '''
    all_fields = ['file_id',
                  'function_id',
                  'date',
                  'added',
                  'changed',
                  'deleted',
                  'nloc',
                  'token_count',
                  'parameter_count',
                  'cyclomatic_complexity']
    try:
        params = _parse_parameters(all_fields, request)
    except ValueError:
        return HttpResponseBadRequest()

    bins = params['bins']
    if bins is None:
        fid_cache, total_values = _get_initial_continous_data(session, params)

        query = session.query(ChangeMetric.function_id).filter(ChangeMetric.date.between(params['from'], params['to']))\
                                                       .order_by(ChangeMetric.date)

        total_data = _get_running_totals(query, params['fields'], fid_cache, total_values, [params['fields']])
    elif bins > 0:
        return HttpResponseBadRequest("Not supported yet")

    elif bins == 0:
        query = session.query(ChangeMetric.function_id).group_by(ChangeMetric.function_id)
        total_data = [params['fields']] + _get_change_metric_snapshot(session, params, query)

    return views_utils.dump_data(total_data, response_type=formating, filename=function_change_metrics.__name__)

@require_GET
@views_utils.session_decorator
def function_defects(session, request, formating='json'):
    '''
    Returns an array of defects for all functions

    See docs/frontends/django_implementation.md for a more detailed description of the format

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
        formating(str):    Indicates wich format that should be returned, [json|csv]
    '''
    all_fields = ['file_id',
                  'function_id',
                  'date',
                  'defect_id']
    try:
        params = _parse_parameters(all_fields, request)
    except ValueError:
        return HttpResponseBadRequest()

    query = _add_defect_query_columns(session, params).filter(DefectModification.date.between(params['from'],
                                                                                              params['to']))\
                                                      .order_by(DefectModification.date)
    if params['bins'] is not None:
        query = query.group_by(DefectModification.function_id)

    return views_utils.dump_data([params['fields']] + query.all(),
                                 response_type=formating,
                                 filename=function_defects.__name__)

@require_GET
@views_utils.session_decorator
def function_id_change_metrics(session, request, function_id, formating='json'):
    '''
    Returns an array of change_metrics for a specific function

    See docs/frontends/django_implementation.md for a more detailed description of the format

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
        function_id:               : the function_id to use as filter
        formating(str):    Indicates wich format that should be returned, [json|csv]
    '''
    all_fields = ['date',
                  'added',
                  'changed',
                  'deleted',
                  'nloc',
                  'token_count',
                  'parameter_count',
                  'cyclomatic_complexity']
    try:
        params = _parse_parameters(all_fields, request)
    except ValueError:
        return HttpResponseBadRequest()

    bins = params['bins']
    if bins is None:
        fid_cache, total_values = _get_initial_continous_data(session, params)

        query = session.query(ChangeMetric.function_id).filter(ChangeMetric.function_id == int(function_id))\
                                                       .filter(ChangeMetric.date.between(params['from'], params['to']))\
                                                       .order_by(ChangeMetric.date)

        total_data = _get_running_totals(query, params['fields'], fid_cache, total_values, [params['fields']])

    elif bins > 0:
        return HttpResponseBadRequest("Not supported yet")

    elif bins == 0:
        query = session.query(ChangeMetric.function_id).filter(ChangeMetric.function_id == int(function_id))
        total_data = [params['fields']] + _get_change_metric_snapshot(session, params, query)

    return views_utils.dump_data(total_data, response_type=formating, filename=function_id_change_metrics.__name__)

@require_GET
@views_utils.session_decorator
def function_id_defects(session, request, function_id, formating='json'):
    '''
    Returns an array of defects for a specific function

    See docs/frontends/django_implementation.md for a more detailed description of the format

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
        function_id:               : the function_id to use as filter
        formating(str):    Indicates wich format that should be returned, [json|csv]
    '''
    all_fields = ['date',
                  'defect_id']
    try:
        params = _parse_parameters(all_fields, request)
    except ValueError:
        return HttpResponseBadRequest()

    query = _add_defect_query_columns(session, params)

    query = query.filter(DefectModification.date.between(params['from'], params['to']))\
                 .filter(DefectModification.function_id == int(function_id))\
                 .order_by(DefectModification.date)

    if params['bins'] is not None:
        query = query.group_by(DefectModification.function_id)

    return views_utils.dump_data([params['fields']] + query.all(),
                                 response_type=formating,
                                 filename=function_id_defects.__name__)

'''
Non view functions
'''
def _get_initial_continous_data(session, params):
    continous_fields = [field for field in params['fields'] if field in MetricsDb.METRICS
                        and MetricsDb.METRICS[field]['continuous']]

    total_values = {field: 0 for field in continous_fields}
    fid_cache = {}

    if len(continous_fields) > 0:
        # Get initial values for all functions
        # We need to do this to get a baseline metric if we are filtering with "from=" clause.
        sq = session.query(ChangeMetric.function_id, func.max(ChangeMetric.date).label('date'))\
                                                    .filter(ChangeMetric.date < params['from'])\
                                                    .group_by(ChangeMetric.function_id)\
                                                    .subquery('prev_nloc')

        query = session.query(ChangeMetric.function_id).filter(and_(ChangeMetric.function_id == sq.c.function_id,
                                                                    ChangeMetric.date == sq.c.date))

        for field in continous_fields:
            query = query.add_columns(replace_null_0(ChangeMetric().columnitems[field]))

        for cm in query:
            fid_cache[cm[0]] = array.array('i', cm[1:])
            for index, field in enumerate(continous_fields):
                total_values[field] += cm[index + 1]

    return fid_cache, total_values

def _get_running_totals(query, cm_fields, fid_cache, cont_values, total_data):
    # Filter out already added columns, and then add remaining, if they are metrics, replace null with 0
    # Skip filtering first column (function_id), since this is a special case and not used when dumping data
    for field in [field for field in cm_fields if field not in [c['name'] for c in query.column_descriptions[1:]]]:
        if field in MetricsDb.METRICS:
            col = replace_null_0(ChangeMetric().columnitems[field])
        else:
            col = ChangeMetric().columnitems[field]
        query = query.add_columns(col)

    column_offset = len(query.column_descriptions) - len(cm_fields)
    for cm in query:
        field_values = []
        continous_index = 0
        '''
        cm[0] == function_id
        cm[1:] == other fields in order they where supplied in the request
        But the continous values do have special consideration that we need to get previous values. To identify
        if its a continous field we check if its part of the cont_values dict, if so, we know its a cont. field.
        Then we have a special cont_index which keeps track and which cont. value to append in the list.
        '''
        prev_values = fid_cache.get(cm[0], array.array('i', (0,) * len(cont_values)))
        for index, field in enumerate(cm_fields):
            # total_values only contain continous values!
            if field in cont_values:
                cont_values[field] += cm[index + column_offset] - prev_values[continous_index]
                prev_values[continous_index] = cm[index + column_offset]
                field_values.append(cont_values[field])
                continous_index += 1
            else:
                field_values.append(cm[index + 1])
        fid_cache[cm[0]] = prev_values
        total_data.append(field_values)
    return total_data

def _get_change_metric_snapshot(session, params, query):
    '''
    Builds 2 queries, one for continous data and one for discontinous data.
    Any non-metric fields gets added to the discontinous query.

    Then we iterate over each query and update an intermediate dictionary, essentially joining both queries into
    a dict with first column as key.
    Then we create a new list where we iterate over the dictionary, but adding fields to the new list in the order
    they where supplied in the fields parameter.

    This is likely very inefficient compared to if we could join both queries, and then directly return the result
    back for transformation. Unfortunatly I have been unable to join queries accuratly due to that continous data
    need to query data over values with date<fields['from'], while discontinous data needs to filter between dates.

    This might be possible using CTE, but I have not yet been able to get that to work accuratly.
    '''
    sq = session.query(ChangeMetric.function_id, func.max(ChangeMetric.date).label('date'))\
                                                .filter(ChangeMetric.date <= params['to'])\
                                                .group_by(ChangeMetric.function_id)\
                                                .subquery('max_func')

    cont_query = query.filter(and_(ChangeMetric.function_id == sq.c.function_id,
                                   ChangeMetric.date == sq.c.date))

    disc_query = query.filter(ChangeMetric.date.between(params['from'], params['to']))

    for field in params['fields']:
        if field in MetricsDb.METRICS:
            colclause = func.sum(replace_null_0(ChangeMetric().columnitems[field])).label(field)
            if MetricsDb.METRICS[field]['continuous']:
                cont_query = cont_query.add_columns(colclause)
            else:
                disc_query = disc_query.add_columns(colclause)
        elif field in ChangeMetric().columnitems:
            colclause = func.max(ChangeMetric().columnitems[field]).label(field)
            disc_query = disc_query.add_columns(colclause)

    data_dict = {}
    for c, d in zip(cont_query, disc_query):
        data_dict.setdefault(c[0], {}).update(c._asdict())
        data_dict.setdefault(d[0], {}).update(d._asdict())

    data = []
    for r in data_dict.itervalues():
        row = []
        for field in params['fields']:
            assert field in r
            row.append(r[field])
        data.append(row)
    return data

def _add_defect_query_columns(session, params):
    '''
    Parses the defect fields and dynamically adds them to query
    '''
    query = None
    for field in params['fields']:
        bins = params['bins']
        if field in DefectModification().columnitems:
            if field in 'defect_id' and bins is not None:
                col = func.count(distinct(DefectModification().columnitems[field]))
            elif field in 'date' and bins is not None:
                col = func.max(DefectModification().columnitems[field])
            else:
                col = DefectModification().columnitems[field]
        elif field in File().columnitems:
            col = File().columnitems[field]

        if query is None:
            query = session.query(col)
        else:
            query = query.add_columns(col)

        if field in File().columnitems:
            query = query.filter(DefectModification.file_id == File.id)

    return query

def _parse_parameters(valid_fields, request):
    '''
    Parses all the possible parameters for any rest request and returns it as a dictionary with either
    param values or defaults.
    If parsing fails it will raise ValueError (for ex. allowing caller to return BadRequest)
    '''
    req_fields = request.GET.get('fields', ','.join(valid_fields)).split(',')
    for field in req_fields:
        if field not in valid_fields:
            raise ValueError
    from_date = views_utils.str2datetime(request.GET.get('from', datetime.datetime.fromtimestamp(0).isoformat()))
    to_date = views_utils.str2datetime(request.GET.get('to', datetime.datetime.now().isoformat()))

    if 'bins' in request.GET:
        bins = int(request.GET.get('bins'))
    else:
        bins = None

    return {'fields': req_fields, 'from': from_date, 'to': to_date, 'bins': bins}
