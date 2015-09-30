#!/usr/bin/env python
# pylint: disable=C0111
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
import unittest
from datetime import datetime
import collections

from DbAPI import MetricsDb
from DbAPI.MetricsDb_ORM import Subsystem, File, Function, Version, User, ChangeMetric, DefectModification
import sqlalchemy


class testMetricsDb(unittest.TestCase):
    def _populate_full_db(self, db):
        with db.get_session() as session:
            ss1 = Subsystem(subsystem='ss1')
            file1 = File(file='file1', subsystem=ss1)
            file2 = File(file='file2', subsystem=ss1)
            function1 = Function(function='function1', file=file1)
            function2 = Function(function='function2', file=file1)
            function3 = Function(function='function3', file=file2)

            file3 = File(file='file3', subsystem=Subsystem(subsystem='ss2'))
            function4 = Function(function='function4', file=file3)

            version1 = Version(version='version1')
            version2 = Version(version='version2')
            version3 = Version(version='version3')
            user1 = User(user='user1')

            session.add(DefectModification(file=file1, version=version1, function=function1, user=user1, defect_id=1,
                                           date=datetime(2000, 1, 1)))
            session.add(DefectModification(file=file1, version=version2, function=function1, user=user1, defect_id=2,
                                           date=datetime(2000, 1, 3)))
            session.add(DefectModification(file=file1, version=version3, function=function1, user=user1, defect_id=3,
                                           date=datetime(2000, 1, 5)))
            session.add(DefectModification(file=file2, version=version1, function=function3, user=user1, defect_id=1,
                                           date=datetime(2000, 1, 1)))

            session.add(DefectModification(file=file3, version=version1, function=function4, user=user1, defect_id=4,
                                           date=datetime(2000, 1, 7)))
            session.add(DefectModification(file=file3, version=version2, function=function4, user=user1, defect_id=5,
                                           date=datetime(2000, 1, 9)))
            session.add(DefectModification(file=file3, version=version3, function=function4, user=user1, defect_id=6,
                                           date=datetime(2000, 1, 11)))

            session.add(ChangeMetric(file=file1, version=version1, function=function1, user=user1,
                                     date=datetime(2000, 1, 1), added=None, changed=1, deleted=100, nloc=1000))
            session.add(ChangeMetric(file=file1, version=version2, function=function1, user=user1,
                                     date=datetime(2000, 1, 3), added=10, changed=1, deleted=200, nloc=2000))
            session.add(ChangeMetric(file=file1, version=version1, function=function2, user=user1,
                                     date=datetime(2000, 1, 5), added=20, changed=1, deleted=300, nloc=3000))
            session.add(ChangeMetric(file=file1, version=version3, function=function2, user=user1,
                                     date=datetime(2000, 1, 7), added=30, changed=1, deleted=400, nloc=4000))

            session.add(ChangeMetric(file=file2, version=version1, function=function3, user=user1,
                                     date=datetime(2000, 1, 7), added=40, changed=1, deleted=500, nloc=5000))
            session.add(ChangeMetric(file=file2, version=version2, function=function3, user=user1,
                                     date=datetime(2000, 1, 9), added=50, changed=1, deleted=600, nloc=6000))
            session.add(ChangeMetric(file=file2, version=version3, function=function3, user=user1,
                                     date=datetime(2000, 1, 11), added=60, changed=1, deleted=700, nloc=7000))

            session.add(ChangeMetric(file=file3, version=version1, function=function4, user=user1,
                                     date=datetime(2000, 1, 2), added=70, changed=1, deleted=800, nloc=8000))
            session.add(ChangeMetric(file=file3, version=version2, function=function4, user=user1,
                                     date=datetime(2000, 1, 3), added=80, changed=1, deleted=900, nloc=9000))
            session.add(ChangeMetric(file=file3, version=version3, function=function4, user=user1,
                                     date=datetime(2000, 1, 4), added=90, changed=1, deleted=1000, nloc=10000))

            session.commit()

    def _add_trs_to_db(self, session):
        file1 = File(file='file1', subsystem=Subsystem(subsystem='ss1'))
        function1 = Function(function='function1', file=file1)
        user1 = User(user='user1')
        tr1 = DefectModification(file=file1, version=Version(version='version1'), function=function1, user=user1,
                                 defect_id=1, date=datetime(2000, 1, 1))

        tr2 = DefectModification(file=file1, version=Version(version='version2'), function=function1, user=user1,
                                 defect_id=2, date=datetime(2000, 1, 3))

        tr3 = DefectModification(file=file1, version=Version(version='version3'), function=function1, user=user1,
                                 defect_id=3, date=datetime(2000, 1, 5))

        testbench = [tr1, tr2, tr3]
        session.add_all(testbench)
        session.commit()

        self.assertListEqual(testbench, session.query(DefectModification).all())

    def test_optimized_datetime(self):
        db = MetricsDb.MetricsDb('sqlite:///:memory:')
        with db.get_session() as session:
            self._add_trs_to_db(session)
            defects = session.query(DefectModification).filter(DefectModification.date.between(datetime(2000, 1, 2),
                                                                                               datetime(2000, 1, 4)))\
                                                                                               .all()
            self.assertEquals(1, len(defects))

    def test_adding_trs_using_add(self):
        db = MetricsDb.MetricsDb('sqlite:///:memory:')
        with db.get_session() as session:
            self._add_trs_to_db(session)
            # This tests the Unique constraint by creating a new File() object but with the same name as
            # the previous one.
            tr1_copy = session.query(DefectModification).first()
            tr1_copy.file = File(file='file1')
            session.add(tr1_copy)
            self.assertRaises(sqlalchemy.exc.IntegrityError, session.commit)
            session.rollback()

    def test_adding_trs_using_wrapper(self):
        db = MetricsDb.MetricsDb('sqlite:///:memory:')
        filename = 'file1'
        version = 'version1'
        function = 'function1'
        defect_id = 1
        user = 'user1'
        date_ = datetime(2000, 1, 3)

        with db.get_session() as session:
            db.insert_defect_modification(session, filename, version, function, defect_id, user, date_)
            defect = session.query(DefectModification).one()
            self.assertEqual(defect.file.file, filename)
            self.assertEqual(defect.version.version, version)
            self.assertEqual(defect.function.function, function)
            self.assertEqual(defect.function.file.file, filename)
            self.assertEqual(defect.defect_id, defect_id)
            self.assertEqual(defect.user.user, user)
            self.assertEqual(defect.date, date_)

            # test uniqueness constraint (adding same defect twice should overwrite)
            db.insert_defect_modification(session, filename, version, function, defect_id, user, date_)
            defect = session.query(DefectModification).one()
            self.assertEqual(defect.file.file, filename)
            self.assertEqual(defect.version.version, version)
            self.assertEqual(defect.function.function, function)
            self.assertEqual(defect.function.file.file, filename)
            self.assertEqual(defect.defect_id, defect_id)
            self.assertEqual(defect.user.user, user)
            self.assertEqual(defect.date, date_)

    def test_adding_change_metric_using_add_all(self):
        db = MetricsDb.MetricsDb('sqlite:///:memory:')
        with db.get_session() as session:
            file1 = File(file='file1')
            function1 = Function(function='function1', file=file1)
            user1 = User(user='user1')
            cm1 = ChangeMetric(file=file1, version=Version(version='version1'), function=function1, user=user1,
                               date=datetime(2000, 1, 1), added=None, changed=1, deleted=250)

            cm2 = ChangeMetric(file=file1, version=Version(version='version2'), function=function1, user=user1,
                               date=datetime(2000, 1, 1), added=None, changed=1, deleted=500)

            cm3 = ChangeMetric(file=file1, version=Version(version='version3'), function=function1, user=user1,
                               date=datetime(2000, 1, 1), added=None, changed=1, deleted=750)

            testbench = [cm1, cm2, cm3]
            session.add_all(testbench)
            session.commit()

            self.assertListEqual(testbench, session.query(ChangeMetric).all())

            # This tests the Unique constraint by creating a new File() object but with the same name as
            # the previous one.
            cm1_copy = cm1
            cm1_copy.file = File(file='file1')
            session.add(cm1_copy)
            self.assertRaises(sqlalchemy.exc.IntegrityError, session.commit)
            session.rollback()

    def test_adding_change_metric_using_wrapper(self):
        db = MetricsDb.MetricsDb('sqlite:///:memory:')
        filename = 'file1'
        version = 'version1'
        function = 'function1'
        user = 'user1'
        date_ = datetime(2000, 1, 3)
        added = 1
        changed = 2
        deleted = 3
        nloc = 4
        token_count = 5
        parameter_count = 6
        cyclomatic_complexity = 7

        with db.get_session() as session:
            db.insert_change_metric(session, filename, version, function, user=user, date_=date_, added=added)
            self.assertTrue(session.query(ChangeMetric).count() == 1)
            cm = session.query(ChangeMetric).one()
            self.assertEqual(cm.file.file, filename)
            self.assertEqual(cm.version.version, version)
            self.assertEqual(cm.function.function, function)
            self.assertEqual(cm.function.file.file, filename)
            self.assertEqual(cm.user.user, user)
            self.assertEqual(cm.added, added)
            self.assertEqual(cm.date, date_)
            self.assertIsNone(cm.changed)
            self.assertIsNone(cm.deleted)
            self.assertIsNone(cm.nloc)
            self.assertIsNone(cm.token_count)
            self.assertIsNone(cm.parameter_count)
            self.assertIsNone(cm.cyclomatic_complexity)

            db.insert_change_metric(session, filename, version, function, changed=changed, deleted=deleted, nloc=nloc,
                                    token_count=token_count, parameter_count=parameter_count,
                                    cyclomatic_complexity=cyclomatic_complexity)

            self.assertTrue(session.query(ChangeMetric).count() == 1)
            cm = session.query(ChangeMetric).one()
            self.assertEqual(cm.file.file, filename)
            self.assertEqual(cm.version.version, version)
            self.assertEqual(cm.function.function, function)
            self.assertEqual(cm.function.file.file, filename)
            self.assertEqual(cm.user.user, user)
            self.assertEqual(cm.date, date_)
            self.assertEqual(cm.added, added)
            self.assertEqual(cm.changed, changed)
            self.assertEqual(cm.deleted, deleted)
            self.assertEqual(cm.nloc, nloc)
            self.assertEqual(cm.token_count, token_count)
            self.assertEqual(cm.parameter_count, parameter_count)
            self.assertEqual(cm.cyclomatic_complexity, cyclomatic_complexity)

    def test_insert_subsystem_entry(self):
        db = MetricsDb.MetricsDb('sqlite:///:memory:')
        with db.get_session() as session:
            ss_name = "ss1"
            ss_status = "maintained"
            ss_maintainers = ['m1', 'm2']
            db.insert_subsystem_entry(session, subsystem=ss_name, status=ss_status, maintainers=ss_maintainers)
            session.commit()

            ss = session.query(Subsystem).filter(Subsystem.subsystem == ss_name).one()
            self.assertEqual(ss.subsystem, ss_name)
            self.assertEqual(ss.status, ss_status)
            self.assertEqual(ss.maintainer, ", ".join(ss_maintainers))

    def test_update_file_entry(self):
        db = MetricsDb.MetricsDb('sqlite:///:memory:')
        with db.get_session() as session:
            file1 = File(file='file1')
            session.add(file1)

            ss1 = Subsystem(subsystem='ss1')
            session.add(ss1)

            session.commit()
            db.update_file_entry(session, file1.id, ss1.subsystem)

            file1 = session.query(File).filter(File.file == file1.file).one()
            self.assertEqual(file1.subsystem, ss1)

    def test_get_changemetric_for_subsystem(self):
        db = MetricsDb.MetricsDb('sqlite:///:memory:')
        self._populate_full_db(db)
        with db.get_session() as session:
            '''
            TRs:
                file1:function1
                    defect_id=1, date=datetime(2000, 1, 1)))
                    defect_id=2, date=datetime(2000, 1, 3)))
                    defect_id=3, date=datetime(2000, 1, 5)))
                file1:function2
                    N/A
                file2:function3
                    defect_id=1, date=datetime(2000, 1, 1)))

            ChangeMetrics:
                file1:function1
                     date=datetime(2000, 1, 1), added=None, changed=1, deleted=100, nloc=1000))
                     date=datetime(2000, 1, 3), added=10, changed=1, deleted=200, nloc=2000))
                file1:function2
                     date=datetime(2000, 1, 5), added=20, changed=1, deleted=300, nloc=3000))
                     date=datetime(2000, 1, 7), added=30, changed=1, deleted=400, nloc=4000))
                file2:function3
                     date=datetime(2000, 1, 7), added=40, changed=1, deleted=500, nloc=5000))
                     date=datetime(2000, 1, 9), added=50, changed=1, deleted=600, nloc=6000))
                     date=datetime(2000, 1, 11), added=60, changed=1, deleted=700, nloc=7000))
            '''
            ss_id = session.query(Subsystem.id).filter(Subsystem.subsystem == 'ss1').scalar()

            testbench_trs = collections.OrderedDict([(datetime(2000, 1, 1), 1),
                                                     (datetime(2000, 1, 3), 1),
                                                     (datetime(2000, 1, 5), 1)])

            # defects is a special case, so explicitly test it
            self.assertEqual(db.get_changemetric_for_subsystem(session, ss_id, 'defect_modifications'), testbench_trs)

            # added is a discontinuous value
            testbench_added = collections.OrderedDict([(datetime(2000, 1, 1), 0),
                                                       (datetime(2000, 1, 3), 10),
                                                       (datetime(2000, 1, 5), 20),
                                                       (datetime(2000, 1, 7), 70),  # 30 + 40 = 70
                                                       (datetime(2000, 1, 9), 50),
                                                       (datetime(2000, 1, 11), 60)])

            self.assertEqual(db.get_changemetric_for_subsystem(session, ss_id, 'added'), testbench_added)

            # nloc is a continuous value
            testbench_nloc = collections.OrderedDict([(datetime(2000, 1, 1), 1000),
                                                      (datetime(2000, 1, 3), 2000),
                                                      (datetime(2000, 1, 5), 5000),  # 2000 + 3000 = 5000
                                                      (datetime(2000, 1, 7), 11000),  # 2000 + 4000 + 5000 = 11000
                                                      (datetime(2000, 1, 9), 12000),  # 2000 + 4000 + 6000 = 12000
                                                      (datetime(2000, 1, 11), 13000)])  # 2000 + 4000 + 7000 = 13000
            self.assertEqual(db.get_changemetric_for_subsystem(session, ss_id, 'nloc'), testbench_nloc)

    def test_get_changemetric_for_file(self):
        db = MetricsDb.MetricsDb('sqlite:///:memory:')
        self._populate_full_db(db)
        with db.get_session() as session:
            file_id = session.query(File.id).filter(File.file == 'file1').scalar()
            '''
            TRs:
                file1:function1
                    defect_id=1, date=datetime(2000, 1, 1)))
                    defect_id=2, date=datetime(2000, 1, 3)))
                    defect_id=3, date=datetime(2000, 1, 5)))
            ChangeMetrics:
                file1:function1
                     date=datetime(2000, 1, 1), added=None, changed=1, deleted=100, nloc=1000))
                     date=datetime(2000, 1, 3), added=10, changed=1, deleted=200, nloc=2000))
                file1:function2
                     date=datetime(2000, 1, 5), added=20, changed=1, deleted=300, nloc=3000))
                     date=datetime(2000, 1, 7), added=30, changed=1, deleted=400, nloc=4000))

            '''
            # Defects is a special case, so explicitly test it
            testbench_trs = collections.OrderedDict([(datetime(2000, 1, 1), 1),
                                                     (datetime(2000, 1, 3), 1),
                                                     (datetime(2000, 1, 5), 1)])

            self.assertEqual(db.get_changemetric_for_file(session, file_id, 'defect_modifications'), testbench_trs)

            # added is a discontinuous value
            testbench_added = collections.OrderedDict([(datetime(2000, 1, 1), 0),
                                                       (datetime(2000, 1, 3), 10),
                                                       (datetime(2000, 1, 5), 20),
                                                       (datetime(2000, 1, 7), 30)])

            self.assertEqual(db.get_changemetric_for_file(session, file_id, 'added'), testbench_added)

            # nloc is a continuous value
            testbench_nloc = collections.OrderedDict([(datetime(2000, 1, 1), 1000),
                                                      (datetime(2000, 1, 3), 2000),
                                                      (datetime(2000, 1, 5), 5000),  # 2000 + 3000 = 5000
                                                      (datetime(2000, 1, 7), 6000)])  # 2000 + 4000 = 6000
            self.assertEqual(db.get_changemetric_for_file(session, file_id, 'nloc'), testbench_nloc)

    def test_get_changemetric_for_function(self):
        db = MetricsDb.MetricsDb('sqlite:///:memory:')
        self._populate_full_db(db)
        with db.get_session() as session:
            function_id = session.query(Function.id).filter(Function.function == 'function1').scalar()
            '''
            TRs: file1:function1
                defect_id=1, date=datetime(2000, 1, 1)))
                defect_id=2, date=datetime(2000, 1, 3)))
                defect_id=3, date=datetime(2000, 1, 5)))

            ChangeMetric file1:function1
                 date=datetime(2000, 1, 1), added=None, changed=1, deleted=100, nloc=1000))
                 date=datetime(2000, 1, 3), added=10, changed=1, deleted=200, nloc=2000))
            '''

            # Defects is a special case, so explicitly test it
            testbench_trs = collections.OrderedDict([(datetime(2000, 1, 1), 1),
                                                     (datetime(2000, 1, 3), 1),
                                                     (datetime(2000, 1, 5), 1)])

            self.assertEqual(db.get_changemetric_for_function(session, function_id, 'defect_modifications'),
                             testbench_trs)

            # added is a discontinuous value
            testbench_added = collections.OrderedDict([(datetime(2000, 1, 3), 10)])  # Since 2000-1-1 added=None
            self.assertEqual(db.get_changemetric_for_function(session, function_id, 'added'), testbench_added)

            # nloc is a continuous value
            testbench_nloc = collections.OrderedDict([(datetime(2000, 1, 1), 1000),
                                                      (datetime(2000, 1, 3), 2000)])
            self.assertEqual(db.get_changemetric_for_function(session, function_id, 'nloc'), testbench_nloc)

    '''
    def test_get_child_components(self):
        db = MetricsDb.MetricsDb('sqlite:///:memory:')
        self._populate_full_db(db)
        with db.get_session() as session:
            ss_id = session.query(Subsystem.id).filter(Subsystem.subsystem == 'ss1').scalar()

            testbench_ss = ['file1', 'file2']
            children = [name for _, name in db.get_child_components(session, ss_id, 'subsystem')]
            self.assertEqual(children, testbench_ss)

            testbench_file = ['function1', 'function2']
            file_id = session.query(File.id).filter(File.file == 'file1').scalar()
            children = [name for _, name in db.get_child_components(session, file_id, 'file')]
            self.assertEqual(children, testbench_file)

    def test_get_subsystems_and_files(self):
        db = MetricsDb.MetricsDb('sqlite:///:memory:')
        self._populate_full_db(db)
        with db.get_session() as session:
            testbench = [{'subsystem': u'ss1', 'id': 1, 'children': [{'id': 1, 'file': u'file1'},
                                                                     {'id': 2, 'file': u'file2'}]},
                         {'subsystem': u'ss2', 'id': 2, 'children': [{'id': 3, 'file': u'file3'}]}]
            subsystems = db.get_subsystems_and_files(session)
            self.assertEqual(subsystems, testbench)
    '''
    def test_eav(self):
        db = MetricsDb.MetricsDb('sqlite:///:memory:')
        now = datetime(2014, 1, 1, 15, 45)
        db.set_eav_value(key='last_update', value=now)
        hopefully_now = db.get_eav_value(key='last_update')
        self.assertEqual(now, hopefully_now)

        another_now = '1-2-3'
        db.set_eav_value(key='last_update', value=another_now)
        hopefully_now = db.get_eav_value(key='last_update')
        self.assertEqual(another_now, hopefully_now)

        some_other_integer = 123
        db.set_eav_value(key='some_other_integer', value=some_other_integer)
        hopefully_some_other_integer = db.get_eav_value(key='some_other_integer')
        self.assertEqual(some_other_integer, hopefully_some_other_integer)

    def test_deletes(self):
        '''
        Tests that deletes automatically removes children
        (Implicitly tests relationship backref clauses)
        '''
        db = MetricsDb.MetricsDb('sqlite:///:memory:')
        self._populate_full_db(db)
        with db.get_session() as session:
            '''
            This should delete file1
            Which should automatically delete function1 & function2
            as well as any defects or changemetrics referencing these files or functions

            You could perform the same operation using query(xxx).delete(), but that
            seems introduce some not-understood caveat with lazy-loading the children.
            i.e the children seem to be still there when querying.
            '''
            for file_ in session.query(File).filter(File.file == 'file1'):
                session.delete(file_)

            all_functions = [fun for fun, in session.query(Function.function)]
            self.assertNotIn('function1', all_functions)
            self.assertNotIn('function2', all_functions)

            tr_files = [defect.file.file for defect in session.query(DefectModification)]
            self.assertNotIn('file1', tr_files)

            tr_functions = [defect.function.function for defect in session.query(DefectModification)]
            self.assertNotIn('function1', tr_functions)
            self.assertNotIn('function2', tr_functions)

            cm_files = [cm.file.file for cm in session.query(ChangeMetric)]
            self.assertNotIn('file1', cm_files)

            cm_functions = [cm.function.function for cm in session.query(ChangeMetric)]
            self.assertNotIn('function1', cm_functions)
            self.assertNotIn('function2', cm_functions)

            '''
            You could perform the same operation using query(xxx).delete(), but that
            seems introduce some not-understood caveat with lazy-loading the children.
            i.e the children seem to be still there when querying.
            '''
            for ss in session.query(Subsystem):
                session.delete(ss)

            testbench = [('file2', None), ('file3', None)]
            files = [(file_.file, file_.subsystem_id) for file_ in session.query(File)]
            self.assertEqual(files, testbench)

    def test_copy_db(self):
        db1 = MetricsDb.MetricsDb('sqlite:///:memory:')
        db2 = MetricsDb.MetricsDb('sqlite:///:memory:')
        self._populate_full_db(db1)
        db2.copy_from_db(db1)

        with db1.get_session() as db1_session, db2.get_session() as db2_session:
            db1_all_files = [(file_.file, file_.subsystem.subsystem) for file_ in db1_session.query(File)]
            db2_all_files = [(file_.file, file_.subsystem.subsystem) for file_ in db2_session.query(File)]

            self.assertEqual(db1_all_files, db2_all_files)

            db1_all_trs = [(defect.file.file, defect.function.function, defect.version.version, defect.defect_id,
                            defect.date, defect.user.user) for defect in db1_session.query(DefectModification)]
            db2_all_trs = [(defect.file.file, defect.function.function, defect.version.version, defect.defect_id,
                            defect.date, defect.user.user) for defect in db2_session.query(DefectModification)]

            self.assertEqual(db1_all_trs, db2_all_trs)

            db1_all_cms = [(cm.file.file, cm.function.function, cm.version.version, cm.user.user, cm.date, cm.added,
                            cm.changed, cm.deleted, cm.nloc, cm.token_count, cm.parameter_count,
                            cm.cyclomatic_complexity)
                           for cm in db1_session.query(ChangeMetric)]

            db2_all_cms = [(cm.file.file, cm.function.function, cm.version.version, cm.user.user, cm.date, cm.added,
                            cm.changed, cm.deleted, cm.nloc, cm.token_count, cm.parameter_count,
                            cm.cyclomatic_complexity)
                           for cm in db2_session.query(ChangeMetric)]

            self.assertEqual(db1_all_cms, db2_all_cms)


if __name__ == "__main__":
    unittest.main()
