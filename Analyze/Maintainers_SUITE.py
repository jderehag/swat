#!/usr/bin/env python
'''
Copyright (c) 2016, Tomas Nilsson  <tomas.w.nilsson@ericsson.com> for Ericsson AB
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
import Maintainers
import os
import shutil
import tempfile
import unittest

def touch(path):
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(path, 'w') as f:
        pass

class testMaintainers(unittest.TestCase):
    def test_maintainers(self):
        try:
            tdir = tempfile.mkdtemp()

            with open(tdir + '/MAINTAINERS', 'w') as f:
                f.write("""
[MAIN]
F:  {0}/main
[UTILS]
F:  {0}/utils
F:  {0}/main/utils
X:  {0}/main/utils/exception.txt
[THIRD]
F:  {0}/main/utils/double.cpp
[FOURTH]
F:  {0}/main/utils/double.cpp
""".format(tdir))

            touch(tdir + '/main/main.cpp') # MAIN
            touch(tdir + '/main/utils/main_utils.cpp') # UTILS (more specific than MAIN)
            touch(tdir + '/unmaintained.cpp') # no maintainer
            touch(tdir + '/ignored.cpp') # ignored (not included below)
            touch(tdir + '/utils/utils.cpp') # UTILS
            touch(tdir + '/main/utils/exception.txt') # MAIN (since excluded by UTIL)
            touch(tdir + '/main/utils/double.cpp') # THIRD and FOURTH

            m = Maintainers.Maintainers(tdir + '/MAINTAINERS')

            no, multi = m.verify_maintainers([
                    tdir + '/main/main.cpp',
                    tdir + '/main/utils/main_utils.cpp',
                    tdir + '/unmaintained.cpp',
                    tdir + '/utils/utils.cpp',
                    tdir + '/main/utils/exception.txt',
                    tdir + '/main/utils/double.cpp',
                    ])

            self.assertEqual(no, [tdir + '/unmaintained.cpp'])
            self.assertEqual(multi, [tdir + '/main/utils/double.cpp'])

            self.assertEqual(m.find_matching_maintainers(tdir + '/main/main.cpp')[0]['subsystem'], 'MAIN')
            self.assertEqual(m.find_matching_maintainers(tdir + '/main/utils/main_utils.cpp')[0]['subsystem'], 'UTILS')
            self.assertEqual(m.find_matching_maintainers(tdir + '/utils/utils.cpp')[0]['subsystem'], 'UTILS')
            self.assertEqual(m.find_matching_maintainers(tdir + '/main/utils/exception.txt')[0]['subsystem'], 'MAIN')
            self.assertEqual([me['subsystem'] for me in m.find_matching_maintainers(tdir + '/main/utils/double.cpp')], ['THIRD', 'FOURTH'])

        finally:
            shutil.rmtree(tdir)

if __name__ == "__main__":
    unittest.main()
