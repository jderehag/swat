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
import ConfigParser
import logging
import multiprocessing
import StringIO
import shutil
import os

from ConfigParser import SafeConfigParser
from __init__ import find_repo_rootdir
from Utils import logger

rootdir = find_repo_rootdir()
default_config = os.path.join(rootdir, 'project.config')
default_config_template = os.path.join(rootdir, 'project.config.template')

defaults = {'General': {'maintainers': None,
                        'lsv_branches': 'main'},

            'Analyze': {'threads': int(multiprocessing.cpu_count() / 2),
                        'engine_url': 'sqlite:///DbAPI/databases/metrics.db',
                        'lookup_email': False,
                        'log_level': 'INFO',
                        'log_path': './messages.log',
                        'log_format': '%%(asctime)s <%%(levelname)s>: %%(message)s'},

            'MetricsViewer': {'engine_url': 'sqlite:///' + os.path.join(rootdir, 'DbAPI', 'databases', 'metrics.db')}}

class _NoValue(object):
    pass

class ProjectConfig(SafeConfigParser):
    '''
    Class that helps with parsing and validating project configs
    '''
    vcs_types = ['Git', 'ClearCase']

    def __init__(self, config=default_config):
        SafeConfigParser.__init__(self)

        self.config = config
        self.defaults = defaults

        if not self._read_config():
            logger.critical('Could not find %s, creating new %s' % (self.config, default_config))
            shutil.copy(default_config_template, default_config)
            logger.critical('Please update %s accordingly!', default_config)
            raise ConfigValidationException

        self._populate_defaults()
        self._validate_config()

    def _read_config(self):
        if isinstance(self.config, StringIO.StringIO):
            self.readfp(self.config)
        else:
            if self.config not in self.read(self.config):
                return False
        return True

    def _populate_defaults(self):
        for section, options in self.defaults.iteritems():
            try:
                self.add_section(section)
            except ConfigParser.DuplicateSectionError:
                pass

            for option, value in options.iteritems():
                if option not in self.options(section):
                    self.set(section, option, str(value))

    def _validate_config(self):
        '''
        Validates the entire project. Each sub validator should print errors as logger.critical and raise AssertionError
        The reason for why we catch it is that we want to print ALL errors before exiting, so that user dont have
        continously iterate like update->run->update->run.
        '''
        sub_validators = [self._validate_vcs]
        success = True

        for validator in sub_validators:
            try:
                validator()
            except AssertionError:
                success = False

        if success is False:
            logger.critical('Validation of %s failed, exiting!' % self.config)
            raise ConfigValidationException

    def get(self, section, option, default_=_NoValue):  # pylint: disable=W0221
        '''
        Gets any section & option, but will return the supplied default value if option is not found.
        '''
        try:
            return SafeConfigParser.get(self, section, option)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
            if default_ is _NoValue:
                raise e
            else:
                return default_

    def getloglevel(self, section, option, default_=_NoValue):
        '''
        Gets loglevel type
        '''
        return getattr(logging, self.get(section, option, default_).upper(), None)  # pylint: disable=E1101

    def getlist(self, section, option, default_=_NoValue):
        '''
        Gets list type
        '''
        result = self.get(section, option, default_)
        if isinstance(result, str):
            result = result.split(os.linesep)  # pylint: disable=E1101
        return result

    def getdict(self, section, option, default_=_NoValue):
        '''
        Gets dict type

        Basically a list, buth with dict-like tuples
        some_option: some_key: some_value
        This could be used as "config.getdict('section', 'some_option') and will return a result as:
        {some_key: some_value}
        '''
        return {transtr.split(':', 1)[0]: transtr.split(':', 1)[1]
                for transtr in self.getlist(section, option, default_)}

    def _validate_vcs(self):
        vcs_backends = [vcs for vcs in ProjectConfig.vcs_types if self.has_section(vcs)]
        if len(vcs_backends) >= 2:
            logger.critical('Found multiple entries for VCS backends, make sure you only have one!')
            logger.critical('VCS backends %s' % ",".join(vcs_backends))
            raise AssertionError

        if len(vcs_backends) <= 0:
            logger.critical('Found NO VCS backends, you must have atleast one!')
            raise AssertionError

    def get_vcs(self):
        '''
        Gets a string representing which VCS backend that should be used.
        Returns:
            vcs(str): either 'Git' or 'ClearCase'
        '''
        return [vcs for vcs in ProjectConfig.vcs_types if self.has_section(vcs)][0]

    def __str__(self):
        output = ''
        for section in self.sections():
            output += '[' + section + ']\n'
            for option, value in self.items(section):
                output += '  ' + option + ': ' + value + '\n'
        return output

class ConfigValidationException(Exception):
    '''
    Raised when config validation failed
    '''
    pass
