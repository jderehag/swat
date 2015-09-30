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

import simplejson as json

from DbAPI.MetricsDb_ORM import Subsystem, File, Function, Version, User
from DbAPI.MetricsDb_ORM import ChangeMetric, DefectModification, DefectMeta
from DbAPI import MetricsDb


def dump_to_json(data):
    return {'json': json.dumps(data)}


class test_views(django.test.SimpleTestCase):
    def test_root(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_get_subsystems(self):
        response = self.client.get('/get_subsystems/', {'response_type': 'application/json'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [['id', 'subsystem'], [1, 'ss1'], [2, 'ss2']])

    def test_get_files_for_subsystem(self):
        response = self.client.get('/get_files_for_subsystem/', {'id': 1, 'response_type': 'application/json'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [['id', 'file'], [1, "file1"], [2, "file2"]])

    def test_get_functions_for_file(self):
        response = self.client.get('/get_functions_for_file/', {'id': 1, 'response_type': 'application/json'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [['id', 'function'], [1, u'function1'], [2, u'function2']])

    def test_treemap(self):
        response = self.client.get('/treemap/')
        self.assertEqual(response.status_code, 200)

    def test_treemap_data(self):
        response = self.client.get('/treemap_data/', {
            'metric': 'defect_modifications',
            'id': 1,
            'type': 'root',
            'response_type': 'application/json'})
        self.assertEqual(response.status_code, 200)
        '''
        Reason for why its 0 is because all defects where created for 2000,
        and query returns now-6months.
        Perhaps API should be modified so that one can request span for the query

        Extend to test all metrics (and not just defect_modifications)
        '''
        self.assertJSONEqual(response.content, [["subsystem", "id", "defect_modifications"],
                                                ["ss1", 1, 0], ["ss2", 2, 0]])

    def test_lineview(self):
        response = self.client.get('/lineview/')
        self.assertEqual(response.status_code, 200)

    def test_lineview_data(self):
        response = self.client.get('/lineview_data/', {
            'id': 1,
            'type': 'subsystem',
            'metric': 'defect_modifications',
            'response_type': 'application/json'})

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [["date", "value"],
                                                [946706400.0, 1], [946879200.0, 1], [947052000.0, 1]])


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
