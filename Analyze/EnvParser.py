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
import re
import os


class EnvPathParser(object):
    '''
    Handles translation of paths, from/to absolute paths to paths containing env. variables
    This will hopefully be removed in the future
    '''
    def __init__(self):
        self._translated_envs = {}

    def parse(self, path):
        '''
        Parses path for environment variables
        '''
        match = re.match(r'.*\$(\w+).*', path)
        if match is not None and match.group(1) is not None:
            try:
                path = path.replace("$" + match.group(1), os.environ[match.group(1)])
                self._translated_envs[match.group(1)] = os.environ[match.group(1)]
            except KeyError:
                pass
        return path

    def translate_to_env(self, path):
        '''
        Takes an absolute path and translates it into original form including env. variables
        '''
        for envname, envpath in self._translated_envs.iteritems():
            if len(envpath) > 0 and envpath in path:
                path = path.replace(envpath, "$" + envname)
        return path
