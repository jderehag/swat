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
  The get_changerate script is used to print the changerate (based any of the lsv branches) for a particular file.
  Typically one would use this script like this:
  > get_changerate.py somedir/somefile.c
  > somedir/somefile.c
  > 2002-04-29  -  0 added, 0 changed, 0 deleted, 916 total
  > 2002-05-29  -  91 added, 57 changed, 12 deleted, 1031 total
  > 2002-12-17  -  27 added, 27 changed, 8 deleted, 1057 total
  > 2003-01-06  -  1 added, 1 changed, 0 deleted, 1058 total
  > 2004-09-22  -  217 added, 84 changed, 3 deleted, 1305 total
  > 2004-09-29  -  16 added, 51 changed, 2 deleted, 1320 total
  ...
'''

import argparse
import os
from Analyze.Backends.VCS import VcsWrapper
from Utils import logger
from Utils.ProjectConfig import ProjectConfig, default_config
from Analyze.Metrics import ChangeRate

help_text = '''The get_changerate script is used to print the changerate (based any of the lsv branches) for a particular file.
               Typically one would use this script like this:
               > get_changerate.py somedir/somefile.c
               > somedir/somefile.c
               > 2002-04-29  -  0 added, 0 changed, 0 deleted, 916 total
               > 2002-05-29  -  91 added, 57 changed, 12 deleted, 1031 total
               > 2002-12-17  -  27 added, 27 changed, 8 deleted, 1057 total
               > 2003-01-06  -  1 added, 1 changed, 0 deleted, 1058 total
               > 2004-09-22  -  217 added, 84 changed, 3 deleted, 1305 total
               > 2004-09-29  -  16 added, 51 changed, 2 deleted, 1320 total
               ...
               '''


class _PathAction(argparse.Action):
    def __call__(self, _, namespace, values, option_string=None):
        setattr(namespace, self.dest, [os.path.abspath(val) for val in values])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=help_text, add_help=True)

    help_str = "Enable verbose output"
    parser.add_argument('-v', action="store_true", dest='verbose', default=False, help=help_str)
    parser.add_argument('--config', dest='config', default=default_config, help="config file")

    help_str = "File(s) to check changerate on"
    parser.add_argument('files', nargs='+', help=help_str, action=_PathAction)
    args = parser.parse_args()

    logger.setup_stdout_logger(args.verbose)

    config = ProjectConfig(config=args.config)
    vcs = VcsWrapper.VcsFactory(config)
    cr = ChangeRate.ChangeRate(vcs)

    for file_ in args.files:
        changerates = cr.count_change_rate_all(file_)
        func_length = len(max([func for entry in changerates for func in entry['changerates'].iterkeys()], key=len))
        func_format = '{: <' + str(func_length + 3) + '}'

        print file_
        for entry in sorted(changerates, key=lambda entry: entry['datetime']):
            print str(entry['datetime'].date())
            for func, (added, changed, deleted, total) in entry['changerates'].iteritems():
                buff = "\t"
                buff += func_format.format(func) + " " + str(added) + " added, " + str(changed) + " changed, "
                buff += str(deleted) + " deleted, " + str(total) + " total"
                print buff
