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
  Generates data for the treemap frontend.

Notes
---

The core of these functions relies on some sort of hierarchical treemap visualization on the frontend.
root            -> generates subsystem data.
subsystem       -> generates file data for all files in that subsystem.
file ->         -> generates function data for all functions in that file.

---

Some functions in this file return queries that focus on a snapshot of the current state (metrics with the most recent
date).
This is somewhat tricky and relies on fetching the most recent metrics from the tables. To do this I'm using a
particular subquery found here: http://stackoverflow.com/a/123481/2966951
The query is database agnostic and fast enough.

Note that the query itself isn't particularly usable because it looks differently in different contexts, i.e in some
cases I filter based on file_ids while in others I don't filter at all. I've tried and failed to make it reusable so
it's repeated with minor variations in many functions and blocks.

---

If the query does not provide a snapshot of the most recent metrics, it provides data over a recent period of time,
i.e defects, No of contributors.

---

The data for defect_modifications and No of contributors is distinct for each level. This means that there can be more
defect_modifications on when viewing the functions in a file, than when viewing the file itself from a subsystem level.
The same goes for a subsystem on a root level. This is because one commit can alter two functions, which is visible
when looking at the functions. But in a file context it is still one commit.
---

Beware of the outer joins in the topmost query (the one that selects the final rows). Usually this is a join with the
subsystem, file or function table (the components). The reasons for this outer join is because change_metrics and
defect_modifications do not share the same subset of components.
To ease up the acess on the frontend, every query must return ALL possible components, even if the metric is NULL.

---

In some of the subqueries on file and function level, the subquery is pre-filtered with the parent component.
* For file level I filter the ChangeMetrics with the file_id.
* For subsystems I fetch all files in the subsystem and perform a ChangeMetric.file_id.in_(files) check.
* For root level nothing is filtered, all of the function data is aggregated to files which in turn aggregates to
  subsystems.

This significantly improves the speed of the query on file/subsystem level, as it doesn't have to loop through all
ChangeMetrics.

*
* -------------------------------------------------------------------------------------------------------------------*/
'''

import __init__  # pylint: disable=W0611

from datetime import datetime
from dateutil.relativedelta import relativedelta

from sqlalchemy import func, and_, case
from sqlalchemy.orm import aliased
from sqlalchemy import cast

from DbAPI.MetricsDb_ORM import Subsystem, File, Function, DefectModification, ChangeMetric
from DbAPI.MetricsDb_ORM import HighPrecisionFloat
from DbAPI.MetricsDb import METRICS


def get_query(session, metric, level, cmp_id):
    '''
    Responds to specific parameters from the view and returns the appropriate query.
    I've decided to put the code here as the types of metrics are tightly coupled to the queries.

    :param session: sqlalchemy.orm.session
    :param metric: str
    :param level: str ["root", "subsystem", "file"]
    :param cmp_id: int
    :return: sqlalchemy.orm.query.Query
    '''
    # Special cases
    if metric == 'defect_modifications':
        query = defect_mods(session, level, cmp_id)
    elif metric == 'effective_complexity':
        query = effective_complexity(session, level, cmp_id)
    elif metric == 'revisions':
        query = revisions(session, level, cmp_id)
    elif metric == 'defect_density':
        query = defect_density(session, level, cmp_id)

    # Generic metrics
    elif METRICS[metric]['continuous']:
        query = _generic_continuous(session, level, metric, cmp_id)
    else:
        query = _generic_discontinuous(session, level, metric, cmp_id)

    return query


def _generic_continuous(session, level, metric, parent_id=None):
    query = None
    cm1 = aliased(ChangeMetric)
    cm2 = aliased(ChangeMetric)
    metric_col = getattr(cm1, metric)

    if level == 'file':
        query = session.query(Function.function,
                              Function.id,
                              replace_null_0(metric_col).label(metric))\
                              .outerjoin(cm1, Function.id == cm1.function_id)\
                              .outerjoin(cm2, and_(cm1.function_id == cm2.function_id, cm1.date < cm2.date))\
                              .filter(cm2.date.is_(None))\
                              .filter(Function.file_id == parent_id)\
                              .order_by(Function.id)

    elif level == 'subsystem':
        query = session.query(File.file,
                              File.id,
                              replace_null_0(func.sum(metric_col)).label(metric))\
                              .outerjoin(cm1, File.id == cm1.file_id)\
                              .outerjoin(cm2, and_(cm1.function_id == cm2.function_id, cm1.date < cm2.date))\
                              .filter(cm2.date.is_(None))\
                              .filter(File.subsystem_id == parent_id)\
                              .group_by(File.id)\
                              .order_by(File.id)

    elif level == 'root':
        query = session.query(Subsystem.subsystem,
                              Subsystem.id,
                              replace_null_0(func.sum(metric_col)).label(metric))\
                              .outerjoin(File, File.subsystem_id == Subsystem.id)\
                              .outerjoin(cm1, File.id == cm1.file_id)\
                              .outerjoin(cm2, and_(cm1.function_id == cm2.function_id, cm1.date < cm2.date))\
                              .filter(cm2.function_id.is_(None))\
                              .group_by(Subsystem.id)\
                              .order_by(Subsystem.id)

    return query


def _generic_discontinuous(session, level, metric, parent_id):
    query = None
    before, now = _get_time_interval()
    metric_col = getattr(ChangeMetric, metric)

    if level == 'file':
        query = session.query(Function.function,
                              Function.id,
                              func.sum(metric_col).label(metric))\
                              .join(ChangeMetric, Function.id == ChangeMetric.function_id)\
                              .filter(ChangeMetric.date.between(before, now))\
                              .filter(ChangeMetric.file_id == parent_id)\
                              .group_by(ChangeMetric.file_id)\
                              .order_by(ChangeMetric.file_id)

    elif level == 'subsystem':
        query = session.query(File.file,
                              File.id,
                              func.sum(metric_col).label(metric))\
                              .outerjoin(ChangeMetric, ChangeMetric.file_id == File.id)\
                              .filter(ChangeMetric.date.between(before, now))\
                              .filter(File.subsystem_id == parent_id)\
                              .group_by(File.id)\
                              .order_by(File.id)

    elif level == 'root':
        query = session.query(Subsystem.subsystem,
                              Subsystem.id,
                              func.sum(metric_col).label(metric))\
                              .outerjoin(File, File.subsystem_id == Subsystem.id)\
                              .outerjoin(ChangeMetric, File.id == ChangeMetric.file_id)\
                              .filter(ChangeMetric.date.between(before, now))\
                              .group_by(Subsystem.id)\
                              .order_by(Subsystem.id)

    return query


def defect_mods(session, level, parent_id=None):
    '''
    Todo: This function is very similar to revisions as it gets
    unique rows for each level in a time interval. Make it more generic?
    '''
    query = None
    before, now = _get_time_interval()

    if level == 'file':
        distinct_per_func = session.query(DefectModification.function_id,
                                          DefectModification.defect_id)\
                                          .filter(DefectModification.date.between(before, now))\
                                          .filter(DefectModification.file_id == parent_id)\
                                          .group_by(DefectModification.function_id, DefectModification.defect_id)\
                                          .subquery()

        query = session.query(Function.function,
                              Function.id,
                              func.count(distinct_per_func.c.defect_id).label("defect_modifications"))\
                              .outerjoin(distinct_per_func, Function.id == distinct_per_func.c.function_id)\
                              .filter(Function.file_id == parent_id)\
                              .group_by(Function.id)\
                              .order_by(Function.id)

    elif level == 'subsystem':
        files = session.query(File.id).filter(File.subsystem_id == parent_id)

        distinct_per_file = session.query(DefectModification.file_id, DefectModification.defect_id).\
            filter(DefectModification.date.between(before, now)).\
            filter(DefectModification.file_id.in_(files)).\
            group_by(DefectModification.file_id, DefectModification.defect_id).\
            subquery()

        query = session.query(
            File.file,
            File.id,
            func.count(distinct_per_file.c.defect_id).label("defect_modifications")
        ).\
            outerjoin(distinct_per_file, File.id == distinct_per_file.c.file_id).\
            filter(File.subsystem_id == parent_id).\
            group_by(File.id).\
            order_by(File.id)

    elif level == 'root':
        distinct_per_subsystem = session.query(
            File.subsystem_id, DefectModification.defect_id
        ).\
            outerjoin(DefectModification, File.id == DefectModification.file_id).\
            filter(DefectModification.date.between(before, now)).\
            group_by(File.subsystem_id, DefectModification.defect_id).\
            subquery()

        query = session.query(
            Subsystem.subsystem,
            Subsystem.id,
            func.count(distinct_per_subsystem.c.defect_id).label("defect_modifications")
        ).\
            outerjoin(distinct_per_subsystem, Subsystem.id == distinct_per_subsystem.c.subsystem_id).\
            group_by(Subsystem.id).\
            order_by(Subsystem.id)

    return query


def revisions(session, level, parent_id=None):
    '''
    Todo: This function is very similar to defect_modifications as it gets
    unique rows for each level in a time interval. Make it more generic?

    :param session: sqlalchemy.orm.session
    :param level: str
    :param parent_id: int
    :return: sqlalchemy.orm.query
    '''
    query = None
    before, now = _get_time_interval()

    if level == 'file':
        distinct_per_func = session.query(
            ChangeMetric.function_id,
            ChangeMetric.version_id
        ).\
            filter(ChangeMetric.date.between(before, now)).\
            filter(ChangeMetric.file_id == parent_id).\
            group_by(ChangeMetric.function_id, ChangeMetric.version_id).\
            subquery()

        query = session.query(
            Function.function,
            Function.id,
            func.count(distinct_per_func.c.function_id).label("revisions")
        ).\
            outerjoin(distinct_per_func, Function.id == distinct_per_func.c.function_id).\
            filter(Function.file_id == parent_id).\
            group_by(Function.id).\
            order_by(Function.id)

    elif level == 'subsystem':
        files = session.query(File.id).filter(
            File.subsystem_id == parent_id)

        distinct_per_file = session.query(
            ChangeMetric.file_id,
            ChangeMetric.version_id
        ).\
            filter(ChangeMetric.date.between(before, now)).\
            filter(ChangeMetric.file_id.in_(files)). \
            group_by(ChangeMetric.file_id, ChangeMetric.version_id).\
            subquery()

        query = session.query(
            File.file,
            File.id,
            func.count(distinct_per_file.c.file_id).label("revisions")
        ).\
            outerjoin(distinct_per_file, File.id == distinct_per_file.c.file_id).\
            filter(File.subsystem_id == parent_id).\
            group_by(File.id).\
            order_by(File.id)

    elif level == 'root':
        distinct_per_subsystem = session.query(
            File.subsystem_id,
            ChangeMetric.version_id
        ).\
            outerjoin(ChangeMetric, File.id == ChangeMetric.file_id).\
            filter(ChangeMetric.date.between(before, now)).\
            group_by(File.subsystem_id, ChangeMetric.version_id).\
            subquery()

        query = session.query(
            Subsystem.subsystem,
            Subsystem.id,
            func.count(distinct_per_subsystem.c.version_id).label("revisions")
        ).\
            outerjoin(distinct_per_subsystem, Subsystem.id == distinct_per_subsystem.c.subsystem_id).\
            group_by(Subsystem.id).\
            order_by(Subsystem.id)

    return query


def effective_complexity(session, level, parent_id=None):
    '''
    Note that on root level the summary is based on all the complexity above 15 / all the complexity.
    This is not the same as calculating all per file and averaging per file to get the avg for a subsystem.

    Args:
        session (sqlalchemy.org.session):       The session used to construct the query
        level (str)                             root|subsystem|file
        parent_id (int)                         The id of the parent component

    Returns:
        sqlalchemy.orm.query
    '''
    query = None
    cm1 = aliased(ChangeMetric)
    cm2 = aliased(ChangeMetric)
    above_15 = case(
        [(cm1.cyclomatic_complexity > 15, cm1.cyclomatic_complexity)]).label('above')

    if level == 'file':
        query = _generic_continuous(
            session, level, 'cyclomatic_complexity', parent_id)

    elif level == 'subsystem':
        query = session.query(
            File.file,
            File.id,
            replace_null_0(func.sum(above_15) * 1.0 / func.sum(cm1.cyclomatic_complexity)).label("effective_complexity")
            ).\
            outerjoin(cm1, File.id == cm1.file_id).\
            outerjoin(cm2, and_(cm1.function_id == cm2.function_id, cm1.date < cm2.date)).\
            filter(cm2.date.is_(None)).\
            filter(File.subsystem_id == parent_id).\
            group_by(File.id).\
            order_by(File.id)

    elif level == 'root':
        query = session.query(
            Subsystem.subsystem,
            Subsystem.id,
            replace_null_0(
                func.sum(above_15) * 1.0 /
                func.sum(cm1.cyclomatic_complexity)).label("effective_complexity")
            ).\
            outerjoin(File, File.subsystem_id == Subsystem.id).\
            outerjoin(cm1, File.id == cm1.file_id).\
            outerjoin(cm2, and_(cm1.function_id == cm2.function_id, cm1.date < cm2.date)).\
            filter(cm2.function_id.is_(None)).\
            group_by(Subsystem.id).\
            order_by(Subsystem.id)

    return query

def defect_density(session, level, parent_id=None):
    '''
    Returns a query for defect density depending on level, defect_density is defined as defects/nloc.

    Args:
        session (sqlalchemy.org.session):       The session used to construct the query
        level (str)                             root|subsystem|file
        parent_id (int)                         The id of the parent component

    Returns:
        sqlalchemy.orm.query
    '''
    query = None
    before, now = _get_time_interval()

    nloc_query = _generic_continuous(session, level, 'nloc', parent_id).subquery()

    if level == 'file':
        distinct_per_func = session.query(DefectModification.function_id,
                                          DefectModification.defect_id)\
                                          .filter(DefectModification.date.between(before, now))\
                                          .filter(DefectModification.file_id == parent_id)\
                                          .group_by(DefectModification.function_id, DefectModification.defect_id)\
                                          .subquery()

        query = session.query(Function.function,
                              Function.id,
                              (cast(func.count(distinct_per_func.c.defect_id), HighPrecisionFloat) /
                               nloc_query.c.nloc).label('defect_density'))\
                              .outerjoin(distinct_per_func, Function.id == distinct_per_func.c.function_id)\
                              .outerjoin(nloc_query, Function.id == nloc_query.c.id)\
                              .filter(Function.file_id == parent_id)\
                              .group_by(Function.id)\
                              .order_by(Function.id)

    elif level == 'subsystem':
        files = session.query(File.id).filter(File.subsystem_id == parent_id)

        distinct_per_file = session.query(DefectModification.file_id,
                                          DefectModification.defect_id)\
                                          .filter(DefectModification.date.between(before, now))\
                                          .filter(DefectModification.file_id.in_(files))\
                                          .group_by(DefectModification.file_id, DefectModification.defect_id)\
                                          .subquery()

        query = session.query(File.file,
                              File.id,
                              (cast(func.count(distinct_per_file.c.defect_id), HighPrecisionFloat) /
                               nloc_query.c.nloc).label('defect_density'))\
                              .outerjoin(distinct_per_file, File.id == distinct_per_file.c.file_id)\
                              .outerjoin(nloc_query, File.id == nloc_query.c.id)\
                              .filter(File.subsystem_id == parent_id)\
                              .group_by(File.id)\
                              .order_by(File.id)

    elif level == 'root':
        distinct_per_subsystem = session.query(File.subsystem_id, DefectModification.defect_id)\
                                    .filter(File.id == DefectModification.file_id,
                                            DefectModification.date.between(before, now))\
                                    .group_by(File.subsystem_id, DefectModification.defect_id)\
                                    .subquery()

        query = session.query(Subsystem.subsystem,
                              Subsystem.id,
                              (cast(func.count(distinct_per_subsystem.c.defect_id), HighPrecisionFloat) /
                               nloc_query.c.nloc).label('defect_density'))\
                             .outerjoin(distinct_per_subsystem, Subsystem.id == distinct_per_subsystem.c.subsystem_id)\
                             .outerjoin(nloc_query, Subsystem.id == nloc_query.c.id)\
                             .group_by(Subsystem.id)\
                             .order_by(Subsystem.id)
    return query

def _get_time_interval(months=6):
    today = datetime.today()
    before = today - relativedelta(months=months)
    return before, today


def replace_null_0(clause):
    '''
    Takes a column and adds a clause so that if value is None then it will be replaced with 0
    '''
    return case([(clause.is_(None), 0)], else_=clause)
