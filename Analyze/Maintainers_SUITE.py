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

            mfile_contents = ""
            mfile_contents += "[MAIN]\n"
            mfile_contents += "F:  {0}\n".format(os.path.join(tdir, 'main'))
            mfile_contents += "[UTILS]\n"
            mfile_contents += "F:  {0}\n".format(os.path.join(tdir, 'utils'))
            mfile_contents += "F:  {0}\n".format(os.path.join(tdir, 'main', 'utils'))
            mfile_contents += "X:  {0}\n".format(os.path.join(tdir, 'main', 'utils', 'exception.txt'))
            mfile_contents += "[THIRD]\n"
            mfile_contents += "F:  {0}\n".format(os.path.join(tdir, 'main', 'utils', 'double.cpp'))
            mfile_contents += "[FOURTH]\n"
            mfile_contents += "F:  {0}\n".format(os.path.join(tdir, 'main', 'utils', 'double.cpp'))
            with open(os.path.join(tdir, 'MAINTAINERS'), 'w') as f:
                f.write(mfile_contents)

            touch(os.path.join(tdir, 'main', 'main.cpp')) # MAIN
            touch(os.path.join(tdir, 'main', 'utils', 'main_utils.cpp')) # UTILS (more specific than MAIN)
            touch(os.path.join(tdir, 'unmaintained.cpp')) # no maintainer
            touch(os.path.join(tdir, 'ignored.cpp')) # ignored (not included below)
            touch(os.path.join(tdir, 'utils', 'utils.cpp')) # UTILS
            touch(os.path.join(tdir, 'main', 'utils', 'exception.txt')) # MAIN (since excluded by UTIL)
            touch(os.path.join(tdir, 'main', 'utils', 'double.cpp')) # THIRD and FOURTH

            m = Maintainers.Maintainers(os.path.join(tdir, 'MAINTAINERS'))

            no, multi = m.verify_maintainers([
                    os.path.join(tdir, 'main', 'main.cpp'),
                    os.path.join(tdir, 'main', 'utils', 'main_utils.cpp'),
                    os.path.join(tdir, 'unmaintained.cpp'),
                    os.path.join(tdir, 'utils', 'utils.cpp'),
                    os.path.join(tdir, 'main', 'utils', 'exception.txt'),
                    os.path.join(tdir, 'main', 'utils', 'double.cpp'),
                    ])

            self.assertEqual(no, [os.path.join(tdir, 'unmaintained.cpp')])
            self.assertEqual(multi, [os.path.join(tdir, 'main', 'utils', 'double.cpp')])

            self.assertEqual(m.find_matching_maintainers(os.path.join(tdir, 'main', 'main.cpp)'))[0]['subsystem'], 'MAIN')
            self.assertEqual(m.find_matching_maintainers(os.path.join(tdir, 'main', 'utils', 'main_utils.cpp'))[0]['subsystem'], 'UTILS')
            self.assertEqual(m.find_matching_maintainers(os.path.join(tdir, 'utils', 'utils.cpp'))[0]['subsystem'], 'UTILS')
            self.assertEqual(m.find_matching_maintainers(os.path.join(tdir, 'main', 'utils', 'exception.txt'))[0]['subsystem'], 'MAIN')
            self.assertEqual([me['subsystem'] for me in m.find_matching_maintainers(os.path.join(tdir, 'main', 'utils', 'double.cpp'))],
                             ['THIRD', 'FOURTH'])

        finally:
            shutil.rmtree(tdir)

if __name__ == "__main__":
    unittest.main()
