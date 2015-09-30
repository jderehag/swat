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

Short description:
'''
import unittest
import argparse
import sys
import os

root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
paths_to_search_for_suites = [root,
                              os.path.join(root, 'www', 'MetricsViewer')]

if root not in sys.path:
    sys.path.append(root)

from Utils import logger

def _run_tests(args, path, pattern):
    loader = unittest.TestLoader().discover(start_dir=path, pattern=pattern)
    print "Running unittests", pattern, "in", path
    result = unittest.runner.TextTestRunner(descriptions=not args.quicktest).run(loader)
    return result.wasSuccessful()


def _initialize():
    for path in paths_to_search_for_suites:
        if path not in sys.path:
            sys.path.append(path)

    '''
    # Initialize django
    '''
    import django
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()



def main():
    # pylint: disable=C0111
    parser = argparse.ArgumentParser(description="Runner for all unittests", add_help=True)
    parser.add_argument('-v', action="store_true", dest='verbose', default=False, help="enable logger, in DEBUG")
    helptext = "Executes minimum of stuff, suitable for commit-hooks and whatnot"
    parser.add_argument('-q', action="store_true", dest='quicktest', default=False, help=helptext)
    helptext = "Executes selenium teststowards a local django server using sqlite as supplied from projects.config"
    parser.add_argument('--selenium', action="store_true", dest='selenium', default=False, help=helptext)
    args = parser.parse_args()
    _initialize()

    if args.verbose:
        logger.setup_stdout_logger(verbose=True)
    else:
        logger.disable_logger()

    was_successful = True
    for path in paths_to_search_for_suites:
        was_successful = _run_tests(args, path=path, pattern="*_SUITE.py") & was_successful

    if args.selenium:
        for path in paths_to_search_for_suites:
            was_successful = _run_tests(args, path=path, pattern="*_LIVESUITE.py") & was_successful

    if was_successful:
        exit(0)
    else:
        print "Unittests failed, fix your crap and rerun", __file__
        exit(-1)

if __name__ == '__main__':
    main()
