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

Short description:
'''
from datetime import datetime
import django.test
from django.conf import settings

from DbAPI.MetricsDb_ORM import Subsystem, File, Function, Version, User
from DbAPI.MetricsDb_ORM import ChangeMetric, DefectModification, DefectMeta
from DbAPI import MetricsDb

class TestViewsRestV0(django.test.SimpleTestCase):
    def test_subsystems(self):
        response = self.client.get('/api/v0/subsystems.json')
        self.assertEqual(response.status_code, 200)
        testbench = [['id', 'subsystem'],
                     [1, 'ss1'],
                     [2, 'ss2']]
        self.assertJSONEqual(response.content, testbench)

    def test_subsystems_changerates_range(self):
        response = self.client.get('/api/v0/subsystems/change_metrics.json')
        self.assertEqual(response.status_code, 200)

        testbench = [["subsystem_id", "date", "added", "changed", "deleted", "nloc", "token_count", "parameter_count",
                      "cyclomatic_complexity"],
                     [1, "2000-01-01T00:00:00", 0, 1, 100, 1000, 0, 0, 0],
                     [2, "2000-01-02T00:00:00", 70, 1, 800, 9000, 0, 0, 0],
                     [1, "2000-01-03T00:00:00", 10, 1, 200, 10000, 0, 0, 0],
                     [2, "2000-01-03T00:00:00", 80, 1, 900, 11000, 0, 0, 0],
                     [2, "2000-01-04T00:00:00", 90, 1, 1000, 12000, 0, 0, 0],
                     [1, "2000-01-05T00:00:00", 20, 1, 300, 15000, 0, 0, 0],
                     [1, "2000-01-07T00:00:00", 30, 1, 400, 16000, 0, 0, 0],
                     [1, "2000-01-07T00:00:00", 40, 1, 500, 21000, 0, 0, 0],
                     [1, "2000-01-09T00:00:00", 50, 1, 600, 22000, 0, 0, 0],
                     [1, "2000-01-11T00:00:00", 60, 1, 700, 23000, 0, 0, 0]]

        self.assertJSONEqual(response.content, testbench)

    def test_subsystems_changerates_bins(self):
        response = self.client.get('/api/v0/subsystems/change_metrics.json?bins=0')
        self.assertEqual(response.status_code, 200)

        testbench = [["subsystem_id", "date", "added", "changed", "deleted", "nloc", "token_count", "parameter_count",
                      "cyclomatic_complexity"],
                     [1, "2000-01-11T00:00:00", 210, 7, 2800, 13000, 0, 0, 0],
                     [2, "2000-01-04T00:00:00", 240, 3, 2700, 10000, 0, 0, 0]]

        self.assertJSONEqual(response.content, testbench)

        response = self.client.get('/api/v0/subsystems/change_metrics.json?bins=1')
        self.assertEqual(response.status_code, 400)


    def test_subsystems_defects_range(self):
        response = self.client.get('/api/v0/subsystems/defects.json')
        self.assertEqual(response.status_code, 200)
        testbench = [["subsystem_id", "date", "defect_id"],
                     [1, "2000-01-01T00:00:00", 1],
                     [1, "2000-01-01T00:00:00", 1],
                     [1, "2000-01-03T00:00:00", 2],
                     [1, "2000-01-05T00:00:00", 3],
                     [2, "2000-01-07T00:00:00", 4],
                     [2, "2000-01-09T00:00:00", 5],
                     [2, "2000-01-11T00:00:00", 6]]
        self.assertJSONEqual(response.content, testbench)

    def test_subsystems_defects_bins(self):
        response = self.client.get('/api/v0/subsystems/defects.json?bins=0')
        self.assertEqual(response.status_code, 200)

        testbench = [["subsystem_id", "date", "defect_id"],
                     [1, "2000-01-05T00:00:00", 3],
                     [2, "2000-01-11T00:00:00", 3]]

        self.assertJSONEqual(response.content, testbench)

    def test_subsystem_id_change_metrics_range(self):
        response = self.client.get('/api/v0/subsystems/1/change_metrics.json')
        self.assertEqual(response.status_code, 200)

        testbench = [["date", "added", "changed", "deleted", "nloc", "token_count", "parameter_count",
                      "cyclomatic_complexity"],
                     ["2000-01-01T00:00:00", 0, 1, 100, 1000, 0, 0, 0],
                     ["2000-01-03T00:00:00", 10, 1, 200, 2000, 0, 0, 0],
                     ["2000-01-05T00:00:00", 20, 1, 300, 5000, 0, 0, 0],
                     ["2000-01-07T00:00:00", 30, 1, 400, 6000, 0, 0, 0],
                     ["2000-01-07T00:00:00", 40, 1, 500, 11000, 0, 0, 0],
                     ["2000-01-09T00:00:00", 50, 1, 600, 12000, 0, 0, 0],
                     ["2000-01-11T00:00:00", 60, 1, 700, 13000, 0, 0, 0]]

        self.assertJSONEqual(response.content, testbench)

    def test_subsystem_id_change_metrics_bins(self):
        response = self.client.get('/api/v0/subsystems/1/change_metrics.json?bins=0')
        self.assertEqual(response.status_code, 200)

        testbench = [["date", "added", "changed", "deleted", "nloc", "token_count", "parameter_count",
                      "cyclomatic_complexity"],
                     ["2000-01-11T00:00:00", 210, 7, 2800, 13000, 0, 0, 0]]

        self.assertJSONEqual(response.content, testbench)

    def test_subsystem_id_function_change_metrics(self):
        response = self.client.get('/api/v0/subsystems/1/function_change_metrics.json')
        self.assertEqual(response.status_code, 200)

        testbench = [["file", "function", "nloc", "cyclomatic_complexity"],
                     ["file1", "function1", 2000, None],
                     ["file1", "function2", 4000, None],
                     ["file2", "function3", 7000, None]]

        self.assertJSONEqual(response.content, testbench)


    def test_subsystem_id_defects_range(self):
        response = self.client.get('/api/v0/subsystems/1/defects.json')
        self.assertEqual(response.status_code, 200)
        testbench = [["date", "defect_id"],
                     ["2000-01-01T00:00:00", 1],
                     ["2000-01-03T00:00:00", 2],
                     ["2000-01-05T00:00:00", 3]]

        self.assertJSONEqual(response.content, testbench)

    def test_subsystem_id_defects_bins(self):
        response = self.client.get('/api/v0/subsystems/1/defects.json?bins=0')
        self.assertEqual(response.status_code, 200)
        testbench = [["date", "defect_id"],
                     ["2000-01-05T00:00:00", 3]]

        self.assertJSONEqual(response.content, testbench)

    def test_files(self):
        response = self.client.get('/api/v0/files.json')
        self.assertEqual(response.status_code, 200)
        testbench = [["subsystem_id", "id", "file"],
                     [1, 1, "file1"],
                     [1, 2, "file2"],
                     [2, 3, "file3"]]
        self.assertJSONEqual(response.content, testbench)

    def test_files_changerates_range(self):
        response = self.client.get('/api/v0/files/change_metrics.json')
        self.assertEqual(response.status_code, 200)

        testbench = [["file_id", "date", "added", "changed", "deleted", "nloc", "token_count", "parameter_count",
                      "cyclomatic_complexity"],
                     [1, "2000-01-01T00:00:00", 0, 1, 100, 1000, 0, 0, 0],
                     [3, "2000-01-02T00:00:00", 70, 1, 800, 9000, 0, 0, 0],
                     [1, "2000-01-03T00:00:00", 10, 1, 200, 10000, 0, 0, 0],
                     [3, "2000-01-03T00:00:00", 80, 1, 900, 11000, 0, 0, 0],
                     [3, "2000-01-04T00:00:00", 90, 1, 1000, 12000, 0, 0, 0],
                     [1, "2000-01-05T00:00:00", 20, 1, 300, 15000, 0, 0, 0],
                     [1, "2000-01-07T00:00:00", 30, 1, 400, 16000, 0, 0, 0],
                     [2, "2000-01-07T00:00:00", 40, 1, 500, 21000, 0, 0, 0],
                     [2, "2000-01-09T00:00:00", 50, 1, 600, 22000, 0, 0, 0],
                     [2, "2000-01-11T00:00:00", 60, 1, 700, 23000, 0, 0, 0]]

        self.assertJSONEqual(response.content, testbench)

    def test_files_changerates_bins(self):
        response = self.client.get('/api/v0/files/change_metrics.json?bins=0')
        self.assertEqual(response.status_code, 200)

        testbench = [["file_id", "date", "added", "changed", "deleted", "nloc", "token_count", "parameter_count",
                      "cyclomatic_complexity"],
                     [1, "2000-01-07T00:00:00", 60, 4, 1000, 6000, 0, 0, 0],
                     [2, "2000-01-11T00:00:00", 150, 3, 1800, 7000, 0, 0, 0],
                     [3, "2000-01-04T00:00:00", 240, 3, 2700, 10000, 0, 0, 0]]

        self.assertJSONEqual(response.content, testbench)

    def test_files_defects_range(self):
        response = self.client.get('/api/v0/files/defects.json')
        self.assertEqual(response.status_code, 200)

        testbench = [["file_id", "date", "defect_id"],
                     [1, "2000-01-01T00:00:00", 1],
                     [2, "2000-01-01T00:00:00", 1],
                     [1, "2000-01-03T00:00:00", 2],
                     [1, "2000-01-05T00:00:00", 3],
                     [3, "2000-01-07T00:00:00", 4],
                     [3, "2000-01-09T00:00:00", 5],
                     [3, "2000-01-11T00:00:00", 6]]
        self.assertJSONEqual(response.content, testbench)

    def test_files_defects_bins(self):
        response = self.client.get('/api/v0/files/defects.json?bins=0')
        self.assertEqual(response.status_code, 200)

        testbench = [["file_id", "date", "defect_id"],
                     [2, "2000-01-01T00:00:00", 1],
                     [1, "2000-01-05T00:00:00", 3],
                     [3, "2000-01-11T00:00:00", 3]]
        self.assertJSONEqual(response.content, testbench)

    def test_file_id_change_metrics_range(self):
        response = self.client.get('/api/v0/files/1/change_metrics.json')
        self.assertEqual(response.status_code, 200)

        testbench = [["date", "added", "changed", "deleted", "nloc", "token_count", "parameter_count",
                      "cyclomatic_complexity"],
                     ["2000-01-01T00:00:00", 0, 1, 100, 1000, 0, 0, 0],
                     ["2000-01-03T00:00:00", 10, 1, 200, 2000, 0, 0, 0],
                     ["2000-01-05T00:00:00", 20, 1, 300, 5000, 0, 0, 0],
                     ["2000-01-07T00:00:00", 30, 1, 400, 6000, 0, 0, 0]]

        self.assertJSONEqual(response.content, testbench)

    def test_file_id_change_metrics_bins(self):
        response = self.client.get('/api/v0/files/1/change_metrics.json?bins=0')
        self.assertEqual(response.status_code, 200)

        testbench = [["date", "added", "changed", "deleted", "nloc", "token_count", "parameter_count",
                      "cyclomatic_complexity"],
                     ["2000-01-07T00:00:00", 60, 4, 1000, 6000, 0, 0, 0]]

        self.assertJSONEqual(response.content, testbench)

    def test_file_id_defects_range(self):
        response = self.client.get('/api/v0/files/1/defects.json')
        self.assertEqual(response.status_code, 200)
        testbench = [["date", "defect_id"],
                     ["2000-01-01T00:00:00", 1],
                     ["2000-01-03T00:00:00", 2],
                     ["2000-01-05T00:00:00", 3]]

        self.assertJSONEqual(response.content, testbench)

    def test_file_id_defects_bins(self):
        response = self.client.get('/api/v0/files/1/defects.json?bins=0')
        self.assertEqual(response.status_code, 200)
        testbench = [["date", "defect_id"],
                     ["2000-01-05T00:00:00", 3]]
        self.assertJSONEqual(response.content, testbench)


    def test_functions(self):
        response = self.client.get('/api/v0/functions.json')
        self.assertEqual(response.status_code, 200)
        testbench = [["file_id", "id", "function"],
                     [1, 1, "function1"],
                     [1, 2, "function2"],
                     [2, 3, "function3"],
                     [3, 4, "function4"]]

        self.assertJSONEqual(response.content, testbench)

    def test_function_changerates_range(self):
        response = self.client.get('/api/v0/functions/change_metrics.json')
        self.assertEqual(response.status_code, 200)

        testbench = [["file_id", "function_id", "date", "added", "changed", "deleted", "nloc", "token_count",
                      "parameter_count", "cyclomatic_complexity"],
                     [1, 1, "2000-01-01T00:00:00", 0, 1, 100, 1000, 0, 0, 0],
                     [3, 4, "2000-01-02T00:00:00", 70, 1, 800, 9000, 0, 0, 0],
                     [1, 1, "2000-01-03T00:00:00", 10, 1, 200, 10000, 0, 0, 0],
                     [3, 4, "2000-01-03T00:00:00", 80, 1, 900, 11000, 0, 0, 0],
                     [3, 4, "2000-01-04T00:00:00", 90, 1, 1000, 12000, 0, 0, 0],
                     [1, 2, "2000-01-05T00:00:00", 20, 1, 300, 15000, 0, 0, 0],
                     [1, 2, "2000-01-07T00:00:00", 30, 1, 400, 16000, 0, 0, 0],
                     [2, 3, "2000-01-07T00:00:00", 40, 1, 500, 21000, 0, 0, 0],
                     [2, 3, "2000-01-09T00:00:00", 50, 1, 600, 22000, 0, 0, 0],
                     [2, 3, "2000-01-11T00:00:00", 60, 1, 700, 23000, 0, 0, 0]]

        self.assertJSONEqual(response.content, testbench)

    def test_function_changerates_bins(self):
        response = self.client.get('/api/v0/functions/change_metrics.json?bins=0')
        self.assertEqual(response.status_code, 200)

        testbench = [["file_id", "function_id", "date", "added", "changed", "deleted", "nloc", "token_count",
                      "parameter_count", "cyclomatic_complexity"],
                     [1, 1, "2000-01-03T00:00:00", 10, 2, 300, 2000, 0, 0, 0],
                     [1, 2, "2000-01-07T00:00:00", 50, 2, 700, 4000, 0, 0, 0],
                     [2, 3, "2000-01-11T00:00:00", 150, 3, 1800, 7000, 0, 0, 0],
                     [3, 4, "2000-01-04T00:00:00", 240, 3, 2700, 10000, 0, 0, 0]]

        self.assertJSONEqual(response.content, testbench)

    def test_function_defects_range(self):
        response = self.client.get('/api/v0/functions/defects.json')
        self.assertEqual(response.status_code, 200)

        testbench = [["file_id", "function_id", "date", "defect_id"],
                     [1, 1, "2000-01-01T00:00:00", 1],
                     [2, 3, "2000-01-01T00:00:00", 1],
                     [1, 1, "2000-01-03T00:00:00", 2],
                     [1, 1, "2000-01-05T00:00:00", 3],
                     [3, 4, "2000-01-07T00:00:00", 4],
                     [3, 4, "2000-01-09T00:00:00", 5],
                     [3, 4, "2000-01-11T00:00:00", 6]]

        self.assertJSONEqual(response.content, testbench)

    def test_function_defects_bins(self):
        response = self.client.get('/api/v0/functions/defects.json?bins=0')
        self.assertEqual(response.status_code, 200)

        testbench = [["file_id", "function_id", "date", "defect_id"],
                     [2, 3, "2000-01-01T00:00:00", 1],
                     [1, 1, "2000-01-05T00:00:00", 3],
                     [3, 4, "2000-01-11T00:00:00", 3]]
        self.assertJSONEqual(response.content, testbench)

    def test_function_id_change_metrics_range(self):
        response = self.client.get('/api/v0/functions/1/change_metrics.json')
        self.assertEqual(response.status_code, 200)

        testbench = [["date", "added", "changed", "deleted", "nloc", "token_count", "parameter_count",
                      "cyclomatic_complexity"],
                     ["2000-01-01T00:00:00", 0, 1, 100, 1000, 0, 0, 0],
                     ["2000-01-03T00:00:00", 10, 1, 200, 2000, 0, 0, 0]]

        self.assertJSONEqual(response.content, testbench)

    def test_function_id_change_metrics_bins(self):
        response = self.client.get('/api/v0/functions/1/change_metrics.json?bins=0')
        self.assertEqual(response.status_code, 200)

        testbench = [["date", "added", "changed", "deleted", "nloc", "token_count", "parameter_count",
                      "cyclomatic_complexity"],
                     ["2000-01-03T00:00:00", 10, 2, 300, 2000, 0, 0, 0]]

        self.assertJSONEqual(response.content, testbench)

    def test_function_id_defects_range(self):
        response = self.client.get('/api/v0/functions/1/defects.json')
        self.assertEqual(response.status_code, 200)
        testbench = [["date", "defect_id"],
                     ["2000-01-01T00:00:00", 1],
                     ["2000-01-03T00:00:00", 2],
                     ["2000-01-05T00:00:00", 3]]

        self.assertJSONEqual(response.content, testbench)

    def test_function_id_defects_bins(self):
        response = self.client.get('/api/v0/functions/1/defects.json?bins=0')
        self.assertEqual(response.status_code, 200)
        testbench = [["date", "defect_id"],
                     ["2000-01-05T00:00:00", 3]]
        self.assertJSONEqual(response.content, testbench)

    def setUp(self):
        db = MetricsDb.MetricsDb('sqlite:///:memory:')
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

            session.add(DefectMeta(id=1, submitted_on=datetime(1999, 1, 1), severity='A', product='LSV',
                                   answer_code='A'))
            session.add(DefectMeta(id=2, submitted_on=datetime(1998, 1, 1), severity='A', product='LSV',
                                   answer_code='A'))
            session.add(DefectMeta(id=3, submitted_on=datetime(1998, 2, 1), severity='A', product='LSV',
                                   answer_code='A'))
            session.add(DefectMeta(id=4, submitted_on=datetime(2000, 1, 1), severity='A', product='LSV',
                                   answer_code='B'))
            session.add(DefectMeta(id=5, submitted_on=datetime(2000, 2, 1), severity='A', product='LSV',
                                   answer_code='B'))
            session.add(DefectMeta(id=6, submitted_on=datetime(2000, 3, 1), severity='A', product='LSV',
                                   answer_code='B'))
            session.add(DefectMeta(id=7, submitted_on=datetime(2005, 1, 1), severity='A', product='LSV',
                                   answer_code='B'))
            session.add(DefectMeta(id=8, submitted_on=datetime(2005, 3, 1), severity='A', product='05',
                                   answer_code='B'))
            session.add(DefectMeta(id=10, submitted_on=datetime(2000, 1, 1), severity='A', product='LSV',
                                   answer_code='D'))
            session.add(DefectMeta(id=11, submitted_on=datetime(2001, 1, 1), severity='A', product='LSV',
                                   answer_code='D'))

            session.commit()
        settings.METRICSDB = db


if __name__ == "__main__":
    import os
    import sys
    import unittest
    import django

    sys.path.append(os.path.abspath('./../'))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'

    django.setup()
    unittest.main()
