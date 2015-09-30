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
from django.views.decorators.http import require_GET
import views_utils

from DbAPI.MetricsDb_ORM import File, Function, ChangeMetric
from sqlalchemy import func


@require_GET
@views_utils.session_decorator
def subsystem_id_nloc_threshold(session, request, subsystem_id, formating='json'):
    '''
    Returns the number of functions that is above threshold for a certain subsystem

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
    '''
    threshold = int(request.GET.get("threshold", "300"))
    thresh_query, total_query = _build_query(session, int(subsystem_id))

    data = {'above_threshold': thresh_query.filter(ChangeMetric.nloc >= threshold).count(),
            'total_functions': total_query.count()}
    return views_utils.dump_data(data, response_type=formating)

@require_GET
@views_utils.session_decorator
def subsystem_id_complexity_threshold(session, request, subsystem_id, formating='json'):
    '''
    Returns the number of functions that is above threshold for a certain subsystem

    Args:
        session(sqlalchemy session): session to use for queries
        request:                   : django request object
    '''
    threshold = int(request.GET.get("threshold", "15"))

    thresh_query, total_query = _build_query(session, int(subsystem_id))

    data = {'above_threshold': thresh_query.filter(ChangeMetric.cyclomatic_complexity >= threshold).count(),
            'total_functions': total_query.count()}

    return views_utils.dump_data(data, response_type=formating)

def _build_query(session, subsystem_id):
    latest_func_sq = session.query(ChangeMetric.function_id, func.max(ChangeMetric.date).label('date'))\
                                                    .group_by(ChangeMetric.function_id)\
                                                    .subquery('latest_func')

    thresh_query = session.query(ChangeMetric, File, Function)\
                                .filter(ChangeMetric.file_id == File.id,
                                        ChangeMetric.function_id == Function.id,
                                        Function.function != '',
                                        File.subsystem_id == subsystem_id,
                                        ChangeMetric.function_id == latest_func_sq.c.function_id,
                                        ChangeMetric.date == latest_func_sq.c.date)\
                                .group_by(ChangeMetric.function_id)

    total_query = session.query(ChangeMetric, File, Function)\
                                .filter(ChangeMetric.file_id == File.id,
                                        ChangeMetric.function_id == Function.id,
                                        Function.function != '',
                                        File.subsystem_id == subsystem_id)\
                                .group_by(ChangeMetric.function_id)
    return thresh_query, total_query
