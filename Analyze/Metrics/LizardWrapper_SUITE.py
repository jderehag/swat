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
  Short description: Test suite for the complexity metrics tool (which currently is https://github.com/terryyin/lizard)
  The output of the tool is tested against a static .c file which has been reviewed manually to find out the correct
  values.
'''
import unittest
import os

import __init__  # pylint: disable=W0611
from LizardWrapper import run_lizard, LizardIndexer


target_test_file = os.path.dirname(__file__) + "/resources/testfile.c"


class testLizardWrapper(unittest.TestCase):
    def test_function_names(self):
        """
        Checks so that the function names in the dictionary the tool outputs are correct.
        """
        correct_function_names = ['firstFunction',
                                  'emptyFunc',
                                  'main',
                                  'bMethodXyz123bb123',
                                  'aMethod123',
                                  'shortFunction',
                                  'methodWithUnnamedReturnStruct']

        function_list = run_lizard(target_test_file)
        self.assertListEqual(correct_function_names, [func['name'] for func in function_list])

    def test_nloc(self):
        """
        Tests number of SLOC source-line-of-code
        """
        correct_NLOC = {'methodWithUnnamedReturnStruct': 14,
                        'firstFunction': 26,
                        'bMethodXyz123bb123': 76,
                        'emptyFunc': 2,
                        'aMethod123': 22,
                        'main': 40,
                        'shortFunction': 1}

        function_list = run_lizard(target_test_file)
        self.assertDictEqual(correct_NLOC, {func["name"]: func["nloc"] for func in function_list})

    def test_mccabe(self):
        """
        Counts the cyclomatic complexity (McCabe) for each function and asserts it
        against the correct value for the target file.
        """
        correct_cyclo = {'methodWithUnnamedReturnStruct': 5,
                         'firstFunction': 11,
                         'bMethodXyz123bb123': 41,
                         'emptyFunc': 1,
                         'aMethod123': 11,
                         'main': 21,
                         'shortFunction': 2}

        function_list = run_lizard(target_test_file)
        result_dict = {func['name']: func["cyclomatic_complexity"] for func in function_list}
        self.assertDictEqual(correct_cyclo, result_dict)

    def test_exclude_python(self):
        self.assertFalse(LizardIndexer.is_analyzable('random.py'))
        self.assertTrue(LizardIndexer.is_analyzable('random.c'))
        self.assertTrue(LizardIndexer.is_analyzable('random.cpp'))


    def runTest(self):
        self.test_function_names()
        self.test_nloc()
        self.test_mccabe()

if __name__ == "__main__":
    unittest.main()
