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
  Test suite for the complexity metrics tool (which currently is https://github.com/terryyin/lizard)
  The output of the tool is tested against a static .c file which has been reviewed manually to find out the correct
  values.
'''
import os
import unittest

from PyDiffer import PyDiffer

cpp_testfile1_0 = os.path.dirname(__file__) + "/resources/testfile1.0.cpp"
cpp_testfile1_1 = os.path.dirname(__file__) + "/resources/testfile1.1.cpp"

cpp_testfile2_0 = os.path.dirname(__file__) + "/resources/testfile_haiku.0.cpp"
cpp_testfile2_1 = os.path.dirname(__file__) + "/resources/testfile_haiku.1.cpp"

class testPyDiffer(unittest.TestCase):
    def test_CPP_added_deleted(self):
        # function: (added, changed, deleted, total)
        # These are incorrect due to that lizard does not handle namespaces.
        # Also, it would seem that it incorrectly identifies func1 as not belonging to Class3.
        testbed = {'': (13, 0, 4, 57),
                   'NS2::Class3::func2': (2, 0, 0, 4),
                   'NS1::Class2::func2': (2, 0, 0, 4),
                   'NS2::Class3::func1': (1, 0, 0, 1),
                   'Class1::func2': (0, 0, 4, 0)}


        stats = PyDiffer(cpp_testfile1_0, cpp_testfile1_1).get_changestat()
        self.assertDictEqual(testbed, stats)

    def test_CPP_changed(self):
        # function: (added, changed, deleted, total)
        testbed = {"func3": (0, 3, 0, 14),
                   "func2": (0, 1, 0, 14),
                   "func6": (0, 1, 6, 8),
                   "main": (0, 1, 0, 14)}
        stats = PyDiffer(cpp_testfile2_0, cpp_testfile2_1).get_changestat()
        self.assertDictEqual(testbed, stats)

    def test_samefile(self):
        testbed = {}
        stats = PyDiffer(cpp_testfile1_0, cpp_testfile1_0).get_changestat()
        self.assertDictEqual(testbed, stats)

    def test_empty_file(self):
        stats = PyDiffer(cpp_testfile2_0, os.devnull).get_changestat()
        testbed = {'': (0, 0, 29, 0),
                   'func2': (0, 0, 14, 0),
                   'func3': (0, 0, 14, 0),
                   'func4': (0, 0, 14, 0),
                   'func5': (0, 0, 14, 0),
                   'func6': (0, 0, 14, 0),
                   'main': (0, 0, 14, 0)}
        self.assertDictEqual(testbed, stats)

        # Once again here we can see that lizard cannot identify if a function is declared in the class definition
        # (or it may be due to that its a oneliner, in either case it hangs up func1 as not belonging to any class
        # or namespace (and since we have 2 functions named func1, they get aggregated.
        stats = PyDiffer(os.devnull, cpp_testfile2_0).get_changestat()
        testbed = {'': (29, 0, 0, 29),
                   'main': (14, 0, 0, 14),
                   'func2': (14, 0, 0, 14),
                   'func3': (14, 0, 0, 14),
                   'func4': (14, 0, 0, 14),
                   'func5': (14, 0, 0, 14),
                   'func6': (14, 0, 0, 14)}

        self.assertDictEqual(testbed, stats)

if __name__ == "__main__":
    unittest.main()
