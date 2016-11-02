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
  The get_maintainer script is used to get which maintainer who is responsible for any piece of code.
  Typically one would use this script like this:
  > get_maintiner.py somedir/somefile.c
  > Subsystem: SomeSubsystem
  > Maintainer: Jesper Derehag <jderehag@hotmail.com>
'''

import argparse
import os

from Utils.ProjectConfig import ProjectConfig, default_config
from Utils import logger

from Analyze import Maintainers, SrcRootWalker

help_text = '''The get_maintainer script is used to get which maintainer who is responsible for any piece of code.
               Typically one would use this script like this:
               > get_maintiner.py somedir/somefile.c
               > Subsystem: SomeSubsystem
               > Maintainer: Jesper Derehag <jderehag@hotmail.com>
               '''


class _PathAction(argparse.Action):
    def __call__(self, _, namespace, values, option_string=None):
        setattr(namespace, self.dest, [os.path.abspath(val) for val in values])

def _parse_args():
    parser = argparse.ArgumentParser(description=help_text, add_help=True)

    help_str = "Verbose printout, mainly for debugging"
    parser.add_argument('-v', action="store_true", dest='verbose', default=False, help=help_str)

    help_str = "config file"
    parser.add_argument('--config', dest='config', default=default_config, help=help_str)

    help_str = "File to check maintainer on"
    parser.add_argument('files', nargs='+', help=help_str, action=_PathAction)

    args = parser.parse_args()
    config = ProjectConfig(config=args.config)
    return args, config

def _main():
    args, config = _parse_args()

    logger.setup_stdout_logger(args.verbose)

    walker = SrcRootWalker.SrcRootWalker(config.getlist('Analyze', 'include_patterns'),
                                         config.getlist('Analyze', 'exclude_patterns', ()))

    # Strips any files that should be excluded
    files = walker.verify_if_files_exist_in_srcroot_paths(args.files)
    maintainerfile = Maintainers.Maintainers(config.get('General', 'maintainers'))

    for file_ in files:
        maintainers = maintainerfile.find_matching_maintainers(file_)
        print "---------------\n", file_, "\n---------------"
        if len(maintainers) == 0:
            print "No maintainer found!"
        else:
            for maintainer in maintainers:
                print "\tSubsystem:\t", maintainer['subsystem']
                print "\tMaintainer:\t",
                print "\n\t           \t".join(["{0} < {1} >".format(person, email)
                                              for person, email in maintainer['maintainer']])
                print "\tMaillist:\t", maintainer['maillist']
                print "\tStatus:\t\t", maintainer['status']

if __name__ == '__main__':
    _main()
