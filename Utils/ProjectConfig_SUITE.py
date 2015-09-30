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
'''
import unittest
import StringIO
import logging
import os
import ConfigParser

import ProjectConfig
from __init__ import repo_root

testconfig = '[General]\n'\
             'filefilters: *.a\n'\
             '             *.so\n'\
             '             *.so.*\n'\
             '             *Some/path*\n'\
             'defect_modification_regexp: *[bug:*|*fix[es]?:*\n'\
             \
             '[Analyze]\n'\
             'threads: 5\n'\
             'dbtype: sqlite\n'\
             'lookup_email: false\n'\
             'log_level:   DEBUG\n'\
             'log_path:   ./some_path_to_log.log\n'\
             'log_format:   %%(asctime)s <%%(levelname)s>: %%(message)s\n'\
             'code_transformer: .sbs: some_path arg1 arg2\n'\
             '                  .random: some_other_path arg1\n'\
             \
             '[Git]\n'\
             'repo:   some_repo_path\n'\
             \
             '[MetricsViewer]\n'\
             'dbtype: sqlite'

testmultioption = \
    '[Filter]\n'\
    'filter:   option1\n'\
    '    option2\n'\
    '    option3\n'\
    'other_option:   option4\n'\
    '[OtherSection]\n'\
    'boolean_option:   True\n'\
    'int_option:   42\n'\
    \
    '[Git]\n'\
    'repo:   some_repo_path\n'


class testProjectConfig(unittest.TestCase):
    def test_complete_config(self):
        config = ProjectConfig.ProjectConfig(StringIO.StringIO(testconfig))

        self.assertEqual(config.getint('Analyze', 'threads'), 5)
        self.assertEqual(config.get('Analyze', 'dbtype'), 'sqlite')
        self.assertEqual(config.getboolean('Analyze', 'lookup_email'), False)
        self.assertEqual(config.getloglevel('Analyze', 'log_level'), logging.DEBUG)
        self.assertEqual(config.get('Analyze', 'log_path'), './some_path_to_log.log')
        self.assertEqual(config.get('Analyze', 'log_format'), '%(asctime)s <%(levelname)s>: %(message)s')
        self.assertEqual(config.getlist('Analyze', 'code_transformer'), ['.sbs: some_path arg1 arg2',
                                                                         '.random: some_other_path arg1'])
        self.assertEqual(config.getlist('General', 'filefilters'), ['*.a', '*.so', '*.so.*', '*Some/path*'])
        self.assertEqual(config.get('General', 'defect_modification_regexp'), '*[bug:*|*fix[es]?:*')

        self.assertEqual(config.get('MetricsViewer', 'dbtype'), 'sqlite')

    def test_config_override(self):
        config = ProjectConfig.ProjectConfig(StringIO.StringIO(testconfig))
        self.assertEqual(config.getloglevel('Analyze', 'log_level'), logging.DEBUG)
        config.set('Analyze', 'log_level', 'CRITICAL')
        self.assertEqual(config.getloglevel('Analyze', 'log_level'), logging.CRITICAL)

    def test_git(self):
        configstr = '[Git]\n'\
                    'path_to_git:   path_to_git\n'\
                    'repo:   some_repo_path\n'

        config = ProjectConfig.ProjectConfig(StringIO.StringIO(configstr))
        self.assertEqual(config.get_vcs(), 'Git')
        self.assertEqual(config.get('Git', 'path_to_git'), 'path_to_git')
        self.assertEqual(config.get('Git', 'repo'), 'some_repo_path')

    def test_clearcase(self):
        configstr = '[ClearCase]\n'\
                    'path_to_cleartool:   cleartool\n'

        config = ProjectConfig.ProjectConfig(StringIO.StringIO(configstr))
        self.assertEqual(config.get_vcs(), 'ClearCase')
        self.assertEqual(config.get('ClearCase', 'path_to_cleartool'), 'cleartool')


    def test_multiple_vcs(self):
        configstr = '[ClearCase]\n'\
                    'include_dirs:   a_dir\n'\
                    \
                    '[Git]\n'\
                    'repo:   some_repo_path\n'

        self.assertRaises(ProjectConfig.ConfigValidationException,
                          ProjectConfig.ProjectConfig, StringIO.StringIO(configstr))

    def test_no_vcs(self):
        self.assertRaises(ProjectConfig.ConfigValidationException,
                          ProjectConfig.ProjectConfig, StringIO.StringIO(''))

    def test_multiline_config(self):
        config = ProjectConfig.ProjectConfig(StringIO.StringIO(testmultioption))
        self.assertEqual(config.getlist('Filter', 'filter'), ['option1', 'option2', 'option3'])
        self.assertEqual(config.get('Filter', 'other_option'), 'option4')

        self.assertEqual(config.getboolean('OtherSection', 'boolean_option'), True)
        self.assertEqual(config.getint('OtherSection', 'int_option'), 42)

    def test_overridden_default(self):
        config = ProjectConfig.ProjectConfig(StringIO.StringIO(testconfig))
        self.assertEqual(config.get('Analyze', 'unknown_attribute', 100), 100)
        self.assertRaises(ConfigParser.NoOptionError, config.get, 'Analyze', 'unknown_attribute')

    def test_all_values_in_template(self):
        realfile = repo_root + "/project.config.template"
        self.assertTrue(os.path.isfile(realfile))
        parser = ProjectConfig.ProjectConfig(config=realfile)

        for def_section, def_options in ProjectConfig.defaults.iteritems():
            self.assertIn(def_section, parser.sections())
            for def_option, _ in def_options.iteritems():
                self.assertTrue(parser.has_option(def_section, def_option))

if __name__ == "__main__":
    from Utils import logger
    logger.disable_logger()
    unittest.main()
