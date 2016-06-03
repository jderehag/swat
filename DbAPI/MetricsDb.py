#!/usr/bin/env python
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
'''
import os
import collections
from contextlib import contextmanager

import __init__  # pylint: disable=W0611
from DbAPI.MetricsDb_ORM import Base, Subsystem, File, Function, Version, User, ChangeMetric, DefectModification, Eav
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, exc
from sqlalchemy.sql.expression import ClauseElement, literal_column
from Utils import logger


METRIC_MAPPING = {'nloc': ChangeMetric.nloc,
                  'added': ChangeMetric.added,
                  'changed': ChangeMetric.changed,
                  'deleted': ChangeMetric.deleted,
                  'token_count': ChangeMetric.token_count,
                  'parameter_count': ChangeMetric.parameter_count,
                  'cyclomatic_complexity': ChangeMetric.cyclomatic_complexity,
                  'max_nesting_depth': ChangeMetric.max_nesting_depth,
                  'fan_in': ChangeMetric.fan_in,
                  'fan_out': ChangeMetric.fan_out,
                  'changerate': ChangeMetric.added + ChangeMetric.changed + ChangeMetric.deleted}

METRICS = {'nloc': {'continuous': True, 'url': '/docs/metrics.md#nloc'},
           'added': {'continuous': False, 'url': '/docs/metrics.md#diff-counts'},
           'changed': {'continuous': False, 'url': '/docs/metrics.md#diff-counts'},
           'deleted': {'continuous': False, 'url': '/docs/metrics.md#diff-counts'},
           'changerate': {'continuous': False, 'url': '/docs/metrics.md#diff-counts'},
           'token_count': {'continuous': True, 'url': '/docs/metrics.md#number-of-tokens'},
           'parameter_count': {'continuous': True, 'url': '/docs/metrics.md#number-of-parameters'},
           'cyclomatic_complexity': {'continuous': True, 'url': '/docs/metrics.md#mccabes-cyclomatic-complexity'},
           'max_nesting_depth': {'continuous': True, 'url': '/docs/metrics.md#max_nesting_depth'},
           'fan_in': {'continuous': True, 'url': '/docs/metrics.md#fan-in'},
           'fan_out': {'continuous': True, 'url': '/docs/metrics.md#fan-out'},
           'effective_complexity': {'continuous': True, 'url': '/docs/metrics.md#effective-cyclomatic-complexity'},
           'defect_modifications': {'continuous': False, 'url': '/docs/metrics.md#defect-modifications'},
           'revisions': {'continuous': False, 'url': '/docs/metrics.md#revisions'},
           'defect_density': {'continuous': True, 'url': '/docs/metrics.md#defect-density'}}


class MetricsDb(object):
    '''
    Manager for the Metrics database
    Handles creation of db, common queries and so on..
    '''
    def __init__(self, enginestr):
        self.engine = create_engine(enginestr, pool_recycle=3600)

        self.metadata = Base.metadata  # pylint: disable=W0201
        self.metadata.bind = self.engine
        self.session = scoped_session(sessionmaker(bind=self.engine))  # pylint: disable=W0201

        try:
            self.metadata.create_all()
        except:
            pass

    def drop_all_tables(self):
        '''
        Drops all tables of this MetricsDb instance
        '''
        self.metadata.drop_all()

    def copy_from_db(self, srcdb):
        '''
        Make a complete copy from srcdb into this instance of MetricsDb
        This drops all tables in this instance and then recreates them, and then populates all tables with data from
        srcdb

        Args:
            srcdb(MetricsDb): The src db to copy from
        '''
        self.drop_all_tables()
        self.metadata.create_all()
        '''
        Since this is a complete copy, we can make some assumptions in terms of foreign-keys etc.
        Therefore, inject all rows directly beeing 100% sure that the foreign-key mapping is identical.
        '''
        for tbl in srcdb.metadata.sorted_tables:
            data = [dict((col.key, x[col.name]) for col in tbl.c) for x in srcdb.engine.execute(tbl.select())]
            if data:
                chunksize = 100000
                for chunk in [data[x:x + chunksize] for x in xrange(0, len(data), chunksize)]:
                    self.engine.execute(tbl.insert(), chunk)

    @contextmanager
    def get_session(self):
        '''
        Yields a session object from the session pool
        '''
        session = self.session()
        try:
            yield session
        finally:
            session.close()

    def get_or_create(self, session, model, defaults=None, **kwargs):
        '''
        Gets an already existing object from the DB, or creates a new one if none exist.
        '''
        instance = session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
            params.update(defaults or {})
            instance = model(**params)
            session.add(instance)
            return instance

    def get_eav_value(self, key):
        '''
        Gets a Entity-attribute-value matching key, if not found returns None
        Args:
            key(str): The key to search for
        Returns:
            eav value: Cast into the correct python type, or None
        '''
        with self.get_session() as session:
            try:
                eav = session.query(Eav).filter(Eav.key == key).one()
            except exc.NoResultFound:
                return None
            else:
                return eav.value

    def set_eav_value(self, key, value):
        '''
        Sets or updates a Entity-attribute-value
        Args:
            key(str): The key to search for
            value(-): The value to set
        '''
        with self.get_session() as session:
            eav = self.get_or_create(session, Eav, key=key)
            eav.value = value
            # We have a commit here due to that we have a local session
            session.commit()

    def insert_defect_modification(self, session, file_, version, function, defect_id, user, date_):
        '''
        Inserts a defect_modification into the database, making sure that all files/functions is created properly.
        Args:
            session(sqlalchemy.session): This is obtained from MetricsDb.get_session
            file_(str): The filename to assign this defect to
            version(str): The filename to assign this defect to
            function(str): The function to assign this defect to
            defect_id(int): The defect id number that this modification is identified by
            user(str): The username of the contributor who committed this defect modification
            date_(datetime): datetime when this modification was done
        '''
        file_ = self.get_or_create(session, File, file=file_)
        version = self.get_or_create(session, Version, version=version)
        function = self.get_or_create(session, Function, function=function, file=file_)

        defect = self.get_or_create(session, DefectModification, file=file_, version=version, function=function)
        defect.defect_id = defect_id
        defect.user = self.get_or_create(session, User, user=user.lower())
        defect.date = date_

    def insert_change_metric(self, session, file_, version, function, date_=None, user=None, added=None,
                             changed=None, deleted=None, nloc=None, token_count=None, parameter_count=None,
                             cyclomatic_complexity=None, max_nesting_depth=None, fan_in=None, fan_out=None):
        '''
        Inserts a ChangeMetric into the database, making sure that all files/functions and whatnot is created properly.
        Args:
            session(sqlalchemy.session): This is obtained from MetricsDb.get_session
            file_(str): The filename to assign this change to
            version(str): The version string to assign this change to
            function(str): The function to assign this change to
            date_(datetime): The date when this change was done
            user(str): The username of the contributor who committed this modification
            added(int): Added lines-of-code
            changed(int): Changed lines-of-code
            deleted(int): Deleted lines-of-code
            nloc(int): number-of-lines-of-code for this function
            token_count(int): number-of-tokens in this function
            parameter_count(int): Number of parameters to this function (arguments)
            cyclomatic_complexity(int): Complexity of this function
        '''
        file_ = self.get_or_create(session, File, file=file_)
        version = self.get_or_create(session, Version, version=version)
        function = self.get_or_create(session, Function, function=function, file=file_)

        cr = self.get_or_create(session, ChangeMetric, file=file_, version=version, function=function)

        if date_ is not None:
            cr.date = date_
        if user is not None:
            cr.user = self.get_or_create(session, User, user=user.lower())
        if added is not None:
            cr.added = added
        if changed is not None:
            cr.changed = changed
        if deleted is not None:
            cr.deleted = deleted
        if nloc is not None:
            cr.nloc = nloc
        if token_count is not None:
            cr.token_count = token_count
        if parameter_count is not None:
            cr.parameter_count = parameter_count
        if cyclomatic_complexity is not None:
            cr.cyclomatic_complexity = cyclomatic_complexity
        if max_nesting_depth is not None:
            cr.max_nesting_depth = max_nesting_depth
        if fan_in is not None:
            cr.fan_in = fan_in
        if fan_out is not None:
            cr.fan_out = fan_out

    def insert_subsystem_entry(self, session, subsystem, status, maintainers):
        '''
        Insert subsystem data to the subsystem table.
        Since the maintainers is a list of maintainers, these are concatented and split by ", "

        Args:
            session(sqlalchemy session): session to use for applying queries
            subsystem(str):     The name of the subsystem
            status(str):        The subsystem maintainance status
            maintainers(list)   List of maintainers
        '''
        maint = self.get_or_create(session, Subsystem, subsystem=subsystem)
        maint.status = status
        maint.maintainer = ", ".join(maintainers).decode("unicode_escape")

    def update_file_entry(self, session, file_id, subsystem_name):
        '''
        Finds the subsystem entry with a certain name, and inserts the id of this subsystem
        into the belonging file entry.

        Args:
            session(sqlalchemy session): session to use for applying queries
            file_id(int):               File id
            subsystem_name(str):        Name of the subsystem
        '''
        ss = session.query(Subsystem).filter(Subsystem.subsystem == subsystem_name).one()
        file_ = session.query(File).filter(File.id == file_id).one()
        file_.subsystem = ss

    def get_file_ids_and_abspaths(self, session):
        '''
        Gets a list of all file_ids and variable expanded file paths

        This function is fairly pointless, (and expandvars should not be part of db wrapper).
        Remove it..

        Returns:
            files(list):         List of all (file id, absolute path)
        '''
        file_id_abspath_list = []
        for file_ in session.query(File):
            file_id_abspath_list.append((file_.id, os.path.expandvars(file_.file)))
        return file_id_abspath_list

    def get_changemetric_for_subsystem(self, session, subsystem_id, metric, continuous=None):
        '''
        This should be rewritten so that it is more agnostic in how it returns the data to the client. It should
        only return the query itself, and not transform it into dictionarys and whatnot.
        The view (who is using this function) makes alot of assumptions as to how the data is returned from here
        and relies that OrmWrapper transforms data so that it fits the view. Any transformations (for the sake of
        clients) should rather instead be done by the views themselves.

        Args:
            session (sqlalchemy.orm.session)
            subsystem_id (int)                  The subsystem for we are fetching data
            metric (str):                       The metric we are fetching data for. Usually this is mapped to a
                                                concrete ORM type in the global METRIC_MAPPING dict.
            continuous (bool)                   Indicates if the metric is continuous or not

        Returns:
            dict:                               A dictionary with the dates and total metric values for the component.
        '''
        total_dict = collections.OrderedDict()

        if continuous is None:
            continuous = METRICS[metric]['continuous']

        if metric == "defect_modifications":
            result = session.query(DefectModification.date, literal_column('1'))\
                            .filter(File.subsystem_id == subsystem_id,
                                    DefectModification.file_id == File.id,
                                    DefectModification.date.isnot(None))\
                            .group_by(DefectModification.version_id).order_by(DefectModification.date)

            for (date_, metric_data) in result:
                total_dict[date_] = metric_data

        else:

            file_ids = session.query(File.id).filter(File.subsystem_id == subsystem_id)
            all_dates = set()
            all_files = {}
            all_files_date = {}

            for file_id, in file_ids:
                for date_, (metric_total) in self.get_changemetric_for_file(session, file_id, metric).iteritems():
                    all_dates.add(date_)
                    all_files.setdefault(file_id, []).append((date_, metric_total))
                    all_files_date.setdefault(date_, []).append((metric_total))

            all_dates = sorted(all_dates)
            '''
            Sort all_entities so that we can assume that dates are *always* in descending
            order, this assumption is later used in calculate_continous()
            '''
            for entrys in all_files.itervalues():
                entrys.sort(key=lambda entry: entry[0], reverse=True)

            for date_ in all_dates:
                if continuous:
                    metric = self._calculate_continuous(all_files, date_)
                else:
                    metric = self._calculate_discontinous(all_files_date, date_)
                total_dict[date_] = metric

        return total_dict

    def get_changemetric_for_file(self, session, file_id, metric, continuous=None):
        '''
        This should be rewritten so that it is more agnostic in how it returns the data to the client. It should
        only return the query itself, and not transform it into dictionarys and whatnot.
        The view (who is using this function) makes alot of assumptions as to how the data is returned from here
        and relies that OrmWrapper transforms data so that it fits the view. Any transformations (for the sake of
        clients) should rather instead be done by the views themselves.

        Args:
            session (sqlalchemy.orm.session)
            file_id (int):                      The file for which the data is gathered
            metric (str):                       The metric we are fetching data for. Usually this is mapped to a
                                                concrete ORM type in the global METRIC_MAPPING dict.
            continuous (bool):                  Indicates wether the metric is continuous or not.

        Returns:
            dict:                               A dictionary with the dates and total metric values for the component
        '''
        total_dict = collections.OrderedDict()

        if continuous is None:
            continuous = METRICS[metric]['continuous']

        if metric == "defect_modifications":
            result = session.query(DefectModification.date, literal_column('1'))\
                            .filter(DefectModification.file_id == file_id,
                                    DefectModification.date.isnot(None))\
                            .group_by(DefectModification.version_id).order_by(DefectModification.date)

            for (date_, metric_data) in result:
                total_dict[date_] = metric_data

        else:
            # Handles generic metrics (nloc, complexity, added...) and changerate
            try:
                metric_column = METRIC_MAPPING[metric]
            except KeyError:
                logger.warn("Incorrect metric supplied, beware of SQL injection attacks! metric=%s", metric)
                return total_dict

            change_metrics = session.query(ChangeMetric.function_id,
                                           ChangeMetric.date,
                                           metric_column).filter(ChangeMetric.file_id == file_id)

            all_dates = set()
            all_functions = {}
            all_functions_date = {}

            for function_id, date_, metric_total in change_metrics:
                if date_ is not None:
                    all_dates.add(date_)
                    all_functions.setdefault(function_id, []).append((date_, metric_total))
                    all_functions_date.setdefault(date_, []).append((metric_total))
            all_dates = sorted(all_dates)
            '''
            Sort all_entities so that we can assume that dates are *always* in descending
            order, this assumption is later used in calculate_continous()
            '''
            for entrys in all_functions.itervalues():
                entrys.sort(key=lambda entry: entry[0], reverse=True)

            for date_ in all_dates:
                if continuous:
                    metric = self._calculate_continuous(all_functions, date_)
                else:
                    metric = self._calculate_discontinous(all_functions_date, date_)
                total_dict[date_] = metric
        return total_dict


    def get_changemetric_for_function(self, session, function_id, metric):
        '''
        This should be rewritten so that it is more agnostic in how it returns the data to the client. It should
        only return the query itself, and not transform it into dictionarys and whatnot.
        The view (who is using this function) makes alot of assumptions as to how the data is returned from here
        and relies that OrmWrapper transforms data so that it fits the view. Any transformations (for the sake of
        clients) should rather instead be done by the views themselves.

        Args:
            session (sqlalchemy.orm.session)
            function_id (int):                  The function for which the data is gathered
            metric (str):                       The metric we are fetching data for. Usually this is mapped to a
                                                concrete ORM type in the global METRIC_MAPPING dict.
            continuous (bool):                  Indicates wether the metric is continuous or not.

        Returns:
            dict:                               A dictionary with the dates and total metric values for the component
        '''
        total_dict = collections.OrderedDict()

        if metric == "defect_modifications":
            result = session.query(DefectModification.date, literal_column('1'))\
                            .filter(DefectModification.function_id == function_id,
                                    DefectModification.date.isnot(None))\
                            .group_by(DefectModification.version_id).order_by(DefectModification.date)

        else:
            try:
                metric_column = METRIC_MAPPING[metric]
            except KeyError:
                logger.warn("Incorrect metric supplied, beware of SQL injection attacks! metric=%s", metric)
                return total_dict

            result = session.query(ChangeMetric.date, metric_column).filter(ChangeMetric.function_id == function_id,
                                                                            ChangeMetric.date.isnot(None),
                                                                            metric_column.isnot(None))\
                            .group_by(ChangeMetric.version_id).order_by(ChangeMetric.date)

        for (date_, metric) in result:
            total_dict[date_] = metric

        return total_dict

    def _calculate_continuous(self, all_entitys, date_):
        '''
        Calculates continous metrics.
        Continous in this case means that a metric is assumed to be the same across versions.
        i.e nloc should be the same for all versions if its not changed. However, the database only stores deltas
        so a simple query with group_by(version_id), would indicate that nloc is 0 in those cases since it would
        contain no data.
        This function is thus used to build a continuing metric across dates.

        Since the database is diff based, function data for a new version is only updated if some function changed.
        This means that the rest of the functions in that file/subsystem are not updated for the new version. To
        retrieve the rest of the data you have to aggregate it from previous entries by iterating over all entries.
        We search backwards for the most recent changemetrics (functions) entries this file should have from previous
        database entries.

        This function assumes that date entry in all_entitys are in descending order with the most recent first.
        Instead of for each iteration, sorting every date entry into a distance vector from requested date,
        we can simply iterate to find the *first* entry that is earlier(or equal) than requested date.

        Args:
            all_entitys (dict):             {function_id: [(date, metric_value)]}
            date_ (ChangeMetric.date):      The date for which we are looking for an earlier entry.

        Returns:
            int:                            The sum of all metric values in an interval of all dates less than the
                                            date_ supplied to the function
        '''
        total_metric = 0

        for entries_for_function in all_entitys.itervalues():
            metric = 0
            # Find the first entry older than date_ for all function entries.
            # This is probably the metric value the function has for this date_.
            for date_value in entries_for_function:
                if date_ >= date_value[0]:
                    metric = date_value[1] or 0
                    break
            total_metric += metric

        return total_metric

    def _calculate_discontinous(self, all_entitys_date, date_):
        '''
        Function that calculates continous metrics for the line chart.
        I.e added, changed, deleted. See add_metric_descriptions()

        Args:
            all_entitys_date (dict):        {function_id: [(_date, metric_value)]}
            date_ (ChangeMetric.date):      The date for which the values are accumulated.

        Returns:
            int:                            The sum of all metric values in an interval of all dates less than the date_
                                            supplied to the function
        '''
        total_metric = 0

        for metric in all_entitys_date[date_]:
            if metric is not None:
                total_metric += metric

        return total_metric
