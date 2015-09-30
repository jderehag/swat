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
from DbAPI.MetricsDb_ORM import ChangeMetric
from DbAPI import MetricsDb

class TestViewsMetaV0(django.test.SimpleTestCase):
    def test_subsystem_id_nloc_threshold(self):
        '''
        ss1:
            file1_global: 1000
            file2_global: 5000
            func1: 2000
            func2: 4000
            func3: 7000
        ss2:
            global: 8000
            func 4: 10000
        '''
        # Default threshold=300
        response = self.client.get('/api/v0/subsystems/1/meta/nloc_threshold.json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'above_threshold': 3, 'total_functions': 3})

        response = self.client.get('/api/v0/subsystems/2/meta/nloc_threshold.json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'above_threshold': 1, 'total_functions': 1})


        def __request(threshold, subsystem, testbench):
            response = self.client.get('/api/v0/subsystems/' + subsystem \
                                       + '/meta/nloc_threshold.json?threshold=' + threshold)
            self.assertEqual(response.status_code, 200)
            self.assertJSONEqual(response.content, testbench)

        __request('3000', '1', {'above_threshold': 2, 'total_functions': 3})
        __request('3000', '2', {'above_threshold': 1, 'total_functions': 1})

        __request('4000', '1', {'above_threshold': 2, 'total_functions': 3})
        __request('4000', '2', {'above_threshold': 1, 'total_functions': 1})

        __request('4001', '1', {'above_threshold': 1, 'total_functions': 3})
        __request('4001', '2', {'above_threshold': 1, 'total_functions': 1})

        __request('8000', '1', {'above_threshold': 0, 'total_functions': 3})
        __request('8000', '2', {'above_threshold': 1, 'total_functions': 1})


    def test_subsystem_id_complexity_threshold(self):
        '''
        ss1:
            file1_global: 10
            file2_global: 50
            func1: 20
            func2: 40
            func3: 70
        ss2:
            global: 80
            func 4: 100
        '''
        # Default threshold=15
        response = self.client.get('/api/v0/subsystems/1/meta/cyclomatic_complexity_threshold.json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'above_threshold': 3, 'total_functions': 3})

        response = self.client.get('/api/v0/subsystems/2/meta/cyclomatic_complexity_threshold.json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'above_threshold': 1, 'total_functions': 1})


        def __request(threshold, subsystem, testbench):
            response = self.client.get('/api/v0/subsystems/' + subsystem \
                                       + '/meta/cyclomatic_complexity_threshold.json?threshold=' + threshold)
            self.assertEqual(response.status_code, 200)
            self.assertJSONEqual(response.content, testbench)

        __request('30', '1', {'above_threshold': 2, 'total_functions': 3})
        __request('30', '2', {'above_threshold': 1, 'total_functions': 1})

        __request('40', '1', {'above_threshold': 2, 'total_functions': 3})
        __request('40', '2', {'above_threshold': 1, 'total_functions': 1})

        __request('41', '1', {'above_threshold': 1, 'total_functions': 3})
        __request('41', '2', {'above_threshold': 1, 'total_functions': 1})

        __request('80', '1', {'above_threshold': 0, 'total_functions': 3})
        __request('80', '2', {'above_threshold': 1, 'total_functions': 1})

    def setUp(self):
        settings.METRICSDB = MetricsDb.MetricsDb('sqlite:///:memory:')

        with settings.METRICSDB.get_session() as session:
            ss1 = Subsystem(subsystem='ss1')
            file1 = File(file='file1', subsystem=ss1)
            file2 = File(file='file2', subsystem=ss1)

            file1_global = Function(function='', file=file1)
            function1 = Function(function='function1', file=file1)
            function2 = Function(function='function2', file=file1)
            file2_global = Function(function='', file=file2)
            function3 = Function(function='function3', file=file2)


            file3 = File(file='file3', subsystem=Subsystem(subsystem='ss2'))
            file3_global = Function(function='', file=file3)
            function4 = Function(function='function4', file=file3)

            version1 = Version(version='version1')
            version2 = Version(version='version2')
            version3 = Version(version='version3')
            user1 = User(user='user1')

            session.add(ChangeMetric(file=file1, version=version1, function=file1_global, user=user1,
                                     date=datetime(2000, 1, 1), nloc=1000, cyclomatic_complexity=10))
            session.add(ChangeMetric(file=file1, version=version1, function=function1, user=user1,
                                     date=datetime(2000, 1, 1), added=None, changed=1, deleted=100, nloc=1000,
                                     cyclomatic_complexity=10))
            session.add(ChangeMetric(file=file1, version=version2, function=function1, user=user1,
                                     date=datetime(2000, 1, 3), added=10, changed=1, deleted=200, nloc=2000,
                                     cyclomatic_complexity=20))
            session.add(ChangeMetric(file=file1, version=version1, function=function2, user=user1,
                                     date=datetime(2000, 1, 5), added=20, changed=1, deleted=300, nloc=3000,
                                     cyclomatic_complexity=30))
            session.add(ChangeMetric(file=file1, version=version3, function=function2, user=user1,
                                     date=datetime(2000, 1, 7), added=30, changed=1, deleted=400, nloc=4000,
                                     cyclomatic_complexity=40))


            session.add(ChangeMetric(file=file2, version=version1, function=file2_global, user=user1,
                                     date=datetime(2000, 1, 7), nloc=5000, cyclomatic_complexity=50))
            session.add(ChangeMetric(file=file2, version=version1, function=function3, user=user1,
                                     date=datetime(2000, 1, 7), added=40, changed=1, deleted=500, nloc=5000,
                                     cyclomatic_complexity=50))
            session.add(ChangeMetric(file=file2, version=version2, function=function3, user=user1,
                                     date=datetime(2000, 1, 9), added=50, changed=1, deleted=600, nloc=6000,
                                     cyclomatic_complexity=60))
            session.add(ChangeMetric(file=file2, version=version3, function=function3, user=user1,
                                     date=datetime(2000, 1, 11), added=60, changed=1, deleted=700, nloc=7000,
                                     cyclomatic_complexity=70))


            session.add(ChangeMetric(file=file3, version=version1, function=file3_global, user=user1,
                                     date=datetime(2000, 1, 2), nloc=8000, cyclomatic_complexity=80))
            session.add(ChangeMetric(file=file3, version=version1, function=function4, user=user1,
                                     date=datetime(2000, 1, 2), added=70, changed=1, deleted=800, nloc=8000,
                                     cyclomatic_complexity=80))
            session.add(ChangeMetric(file=file3, version=version2, function=function4, user=user1,
                                     date=datetime(2000, 1, 3), added=80, changed=1, deleted=900, nloc=9000,
                                     cyclomatic_complexity=90))
            session.add(ChangeMetric(file=file3, version=version3, function=function4, user=user1,
                                     date=datetime(2000, 1, 4), added=90, changed=1, deleted=1000, nloc=10000,
                                     cyclomatic_complexity=100))

            session.commit()



if __name__ == "__main__":
    import os
    import sys
    import unittest
    import django

    sys.path.append(os.path.abspath('./../'))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'

    django.setup()
    unittest.main()
