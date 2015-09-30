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
  The get_defects.py script is used to list the defect fixes contributed to a particular file.
  > get_defects.py somedir/somefile.c
    somedir/somfile.c
        2002-03-06      defect_id:  1923       somename1
        2003-07-29      defect_id:  4252       somename2
        2003-09-12      defect_id:  4497       somename1
        2004-03-25      defect_id:  5000       somename1
        2004-05-19      defect_id:  5423       somename1
        ...
*
* -------------------------------------------------------------------------------------------------------------------*/
'''

import argparse
import os
from Analyze.Backends.VCS import VcsWrapper
from Utils import logger
from Utils.ProjectConfig import ProjectConfig, default_config

from datetime import datetime, time

help_text = '''The get_defects.py script is used to list the defect fixes contributed to a particular file.
               > get_defects.py somedir/somefile.c
               somedir/somfile.c
               2002-03-06      defect_id:  1923       somename1
               2003-07-29      defect_id:  4252       somename2
               2003-09-12      defect_id:  4497       somename1
               2004-03-25      defect_id:  5000       somename1
               2004-05-19      defect_id:  5423       somename1
               ...
               '''


class _PathAction(argparse.Action):
    def __call__(self, _, namespace, values, option_string=None):
        setattr(namespace, self.dest, [os.path.abspath(val) for val in values])

def _mkdate(datestring):
    return datetime.combine(datetime.strptime(datestring, '%Y-%m-%d').date(), time())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=help_text, add_help=True)

    help_str = "Verbose, print (non)-matching branches and do a proper describe of each defect."
    parser.add_argument('-v', action="store_true", dest='verbose', default=False, help=help_str)

    help_str = "Prints changed functions for each defect"
    parser.add_argument('--changeset', action="store_true", dest='changeset', default=False, help=help_str)

    help_str = "Prints defect per changed function"
    parser.add_argument('--function', action="store_true", dest='function', default=False, help=help_str)

    help_str = "Show only defects since date <YYYY-MM-DD> (default: all defects)"
    parser.add_argument('-s', type=_mkdate, dest='since', default=None, help=help_str)

    parser.add_argument('--config', dest='config', default=default_config, help="config file")

    help_str = "File(s) to check number of defects on"
    parser.add_argument('files', nargs='+', help=help_str, action=_PathAction)
    args = parser.parse_args()

    logger.setup_stdout_logger(args.verbose)

    config = ProjectConfig(config=args.config)
    vcs = VcsWrapper.VcsFactory(config)

    for file_ in args.files:
        print file_

        if args.changeset:
            defects = vcs.find_all_defects(file_, args.since, changeinfo=True)

            for defect, defect_info in defects.iteritems():
                earliest_entry = sorted(defect_info, key=lambda(defect_info): defect_info['datetime'])[0]
                print "\t", str(earliest_entry['datetime'].date()), "\tDefect: ", defect, "\t", earliest_entry['user']
                print "\tAffected functions:"
                functions = [function for patch in defect_info for function in patch['functions']]
                for function in functions:
                    print "\t\t", function

        elif args.function:
            defects = vcs.find_all_defects(file_, args.since, changeinfo=True)
            function_dict = {}
            for defect, defect_info in defects.iteritems():
                for patch in defect_info:
                    for function in patch['functions']:
                        function_dict.setdefault(function, []).append(defect)

            for function, defects in sorted(function_dict.iteritems(), reverse=True,
                                            key=lambda(function, defects): len(defects)):
                if args.verbose:
                    print '{:<40}'.format(function)
                    for defect in defects:
                        print "\t", defect
                else:
                    print '{:<50}'.format(function), len(defects)

        else:
            defects = vcs.find_all_defects(file_, args.since)
            only_first_versions_of_elements = []
            for defect, elems in defects.iteritems():
                only_first_versions_of_elements.append((defect, sorted(elems, key=lambda(elem): elem['datetime'])[0]))

            only_first_versions_of_elements.sort(key=lambda(defect, elem): elem['datetime'])
            for defect, elem in only_first_versions_of_elements:
                print "\t", str(elem['datetime'].date()), "\tdefect_id: ", defect, "\t", elem['user']
