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
from fnmatch import fnmatch
import re
import os
from Utils import logger
from Analyze import EnvParser
import codecs


class Maintainers(object):
    """
    Takes a maintainerfile and parses it.
    Exits application if maintainerfile could not be opened.
    """

    def __init__(self, maintainerfile):
        self._maintainerfile = maintainerfile
        self._maintainer_entrys = []
        self._env_parser = EnvParser.EnvPathParser()

        try:
            file_ = codecs.open(self._maintainerfile, encoding='utf-8', mode='r')
        except IOError:
            logger.critical("Could not open %s this should be impossible at this stage!", self._maintainerfile)
            exit(-1)

        maintainerfile = []

        # Filter out empty lines and comments
        while 1:
            lines = file_.readlines()
            if not lines:
                break
            for line in lines:
                if len(line.lstrip()) != 0:
                    if line.lstrip()[0] != '#':
                        maintainerfile.append(line.strip().encode('utf-8'))
        self._read_maintainer_scopes(maintainerfile)
        self._verify_paths()

    def _verify_paths(self):
        is_ok = True

        filepaths = []
        for maint in self.get_maintainer_list():
            filepaths.extend(maint['file-include-pattern'])
            filepaths.extend(maint['file-exclude-pattern'])

        all_envs = {}
        for path in filepaths:
            match = re.match(r'.*\$(\w+).*', path)
            if match is not None and match.group(1) is not None:
                all_envs[match.group(1)] = None

        for env in all_envs.iterkeys():
            if env not in os.environ:
                logger.critical("Could not find $%s envrionment variable! Perhaps you need to run setup_workspace?",
                                env)
                is_ok = False

        assert is_ok

    def get_maintainer_list(self):
        """
        Returns the parsed maintainerlist.

        Args:
            None
        Returns:
            maintainerentrys(list(entry)): entry(dict) =
                                            entry['subsystem'](str)
                                            entry['maintainer'](list(str))
                                            entry['maillist'](str)
                                            entry['status'](str)
                                            entry['file-include-pattern'](list(str))
                                            entry['file-exclude-pattern'](list(str))

        Raises:
            None

        """
        return self._maintainer_entrys

    def get_maintainer_entry(self, subsystem_name):
        """
        Searches for a maintainer entry matching subsystem.

        Args:
            subsystem_name(str): name of the subsystem to try to find the entry for
        Returns:
            subsystem entry(dict):
                                entry['subsystem'](str)
                                entry['maintainer'](list(str))
                                entry['maillist'](str)
                                entry['status'](str)
                                entry['file-include-pattern'](list(str))
                                entry['file-exclude-pattern'](list(str))

        Raises:
            None
        """
        for entry in self.get_maintainer_list():
            if entry['subsystem'] == subsystem_name:
                return entry
        return None

    def find_matching_maintainers(self, filename):
        """
        Searches for any maintainer responsible for filename

        Really not happy with this implementation, basically does a linear search finding matches.
        Should instead be implemented using radix tree..

        Args:
            filename(str): name of the file to check responsibility for
        Returns:
            matching_maintainer(list): entry(dict):
                                            entry['subsystem'](str)
                                            entry['maintainer'](list(str))
                                            entry['maillist'](str)
                                            entry['status'](str)
                                            entry['file-include-pattern'](list(str))
                                            entry['file-exclude-pattern'](list(str))
        Raises:
            None
        """
        matching_maintainers = []
        for maintainer in self.get_maintainer_list():
            do_exclude = False
            # First check exclude pattern
            for exclpattern in maintainer['file-exclude-pattern']:
                if exclpattern[-1:] == '/':  # Handle this like a catch-all recursive directory rule
                    if filename.startswith(exclpattern):
                        do_exclude = True
                        logger.debug('Excluding "%s" based on, rule=%s', maintainer['subsystem'], exclpattern)
                else:
                    if fnmatch(filename, exclpattern):
                        do_exclude = True
                        logger.debug('Excluding "%s" based on, rule=%s', maintainer['subsystem'], exclpattern)

            # Then check include pattern
            if do_exclude is False:
                for inclpattern in maintainer['file-include-pattern']:
                    if filename[1] == '/':  # Handle this as an absolute path
                        if filename.endswith(inclpattern):
                            logger.debug('Found match for "%s", rule=%s', maintainer['subsystem'], inclpattern)
                            matching_maintainers.append(maintainer)
                    elif inclpattern[-1:] == '/':  # Handle this like a catch-all recursive directory rule
                        if inclpattern in filename:
                            logger.debug('Found match for "%s", rule=%s', maintainer['subsystem'], inclpattern)
                            matching_maintainers.append(maintainer)
                    elif fnmatch(filename, inclpattern):
                        logger.debug('Found match for "%s", rule=%s', maintainer['subsystem'], inclpattern)
                        matching_maintainers.append(maintainer)
        return matching_maintainers

    def _read_maintainer_scopes(self, text):
        # Really not happy with this parsing,
        # should be much easier doing it properly using recursion
        # Actually, investigate if this entire class can be changed so that it used ConfigParser instead, but *must*
        # keep original linux kernel MAINTAINERS file structure!
        line_index = 0
        while line_index in range(0, len(text)):
            if text[line_index][0] == '[':  # scope begin!
                maintainer_scope = []
                maintainer_scope.append(text[line_index])
                line_index = line_index + 1
                # Get all lines below "scope begin" until we reach next scope
                while line_index in range(0, len(text)):
                    if text[line_index][0] != '[':
                        maintainer_scope.append(text[line_index])
                        line_index = line_index + 1
                    else:

                        break
                self._maintainer_entrys.append(self._parse_maintainer_scope(maintainer_scope))
            else:
                line_index = line_index + 1

    def _parse_maintainer_scope(self, text):
        maintainer = {}
        maintainer['subsystem'] = ""
        maintainer['maintainer'] = []
        maintainer['maillist'] = ""
        maintainer['status'] = ""
        maintainer['file-include-pattern'] = []
        maintainer['file-exclude-pattern'] = []

        for lnumber, line in enumerate(text):
            if line[0] == '[':  # subsystem name
                maintainer['subsystem'] = line[1:line.rfind(']')].strip()
            elif line[0:2] == 'M:':  # Maintainer
                maintainer['maintainer'].append((line[2:line.find('<')].strip(),
                                                 line[line.find('<') + 1:line.find('>')].strip()))
            elif line[0:2] == 'L:':  # mailinglist
                maintainer['maillist'] = line[2:].strip()
            elif line[0:2] == 'S:':  # Status
                maintainer['status'] = line[2:].strip()
            elif line[0:2] == 'F:':  # File pattern
                maintainer['file-include-pattern'].append(self._env_parser.parse(line[2:].strip()))
            elif line[0:2] == 'X:':  # Exclude pattern
                maintainer['file-exclude-pattern'].append(self._env_parser.parse(line[2:].strip()))
            else:
                logger.warn("Unable to intrpret line %s [must start with one of [MLSFX :[%s]", lnumber, line)
        return maintainer
