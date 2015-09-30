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
  The get_contributor script is used to get which designer which made the biggest contributions to a particular file.
  Typically one would use this script like this:
  > get_contributor.py somedir/somefile.c
  > somedir/somefile.c
  > Contributor:   jeppe       jderehag@hotmail.com                     check-ins: 7% 107/1408
  > Contributor:   randomuser  N/A                                      check-ins: 4% 67/1408
  > Contributor:   randomuser2 randomuser2@somedomain.com               check-ins: 3% 54/1408
  ...
'''

import argparse
import os
from datetime import datetime, date, timedelta
from Analyze.Backends.VCS import VcsWrapper
from Analyze.Backends.LdapWrapper import LdapWrapper
from Utils import logger
from Utils.ProjectConfig import ProjectConfig, default_config

help_text = '''The get_contributor script is used to get which designer which made the biggest contributions to a particular file.
               Typically one would use this script like this:
               > get_contributor.py somedir/somefile.c
               > somedir/somefile.c
               > Contributor:   jeppe       jderehag@hotmail.com                     check-ins: 7% 107/1408
               > Contributor:   randomuser  N/A                                      check-ins: 4% 67/1408
               > Contributor:   randomuser2 randomuser2@somedomain.com               check-ins: 3% 54/1408
               ...
               '''

class _PathAction(argparse.Action):
    def __call__(self, _, namespace, values, option_string=None):
        setattr(namespace, self.dest, [os.path.abspath(val) for val in values])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=help_text, add_help=True)
    help_str = "Try and lookup email WARN: unstable! (default: NO)"
    parser.add_argument('-e', action="store_true", dest='email', default=False, help=help_str)

    help_str = "Lookup contributions *since* date <YYYY-MM-DD> (default: -3 years)"
    parser.add_argument('-s', dest='since', default=None, help=help_str)

    parser.add_argument('--config', dest='config', default=default_config, help="config file")

    help_str = "File to check contributor on"
    parser.add_argument('files', nargs='+', help=help_str, action=_PathAction)
    args = parser.parse_args()

    logger.setup_stdout_logger()

    config = ProjectConfig(config=args.config)
    vcs = VcsWrapper.VcsFactory(config)
    ldapWrapper = LdapWrapper.LdapWrapper()

    for file_ in args.files:
        outputstring = file_ + "\n"
        if args.since is not None:
            since = datetime.strptime(args.since, '%Y-%m-%d')
            contributors, number_of_checkins = vcs.find_contributors(file_, since)
        else:
            since_date = date.today() - timedelta(days=365 * 3)
            contributors, number_of_checkins = vcs.find_contributors(file_, since_date)

        for name, value in contributors[0:10]:
            outputstring += 'Contributor:   '
            outputstring += '{: <30}'.format(name)
            if args.email:
                outputstring += '{: <40}'.format(ldapWrapper.get_email(name))
            outputstring += " check-ins: " + str(int(float(value) / number_of_checkins * 100)) \
                            + "% " + str(value) + "/" + str(number_of_checkins) + "\n"
        print outputstring
