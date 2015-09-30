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
import os
import re
from fnmatch import fnmatch
from Utils import logger
from Analyze import EnvParser


class SrcRootWalker(object):
    """
    Takes a src-root-file and parses it.
    Exits application if srcRootFile could not be opened.
    """
    def __init__(self, include_patterns, exclude_patterns):
        self._env_parser = EnvParser.EnvPathParser()
        self._srcroots_include = [self._env_parser.parse(line) for line in include_patterns]
        self._srcroots_exclude = [self._env_parser.parse(line) for line in exclude_patterns]
        self._verify_paths()

    def _verify_paths(self):
        is_ok = True
        all_envs = {}
        for path in self._srcroots_include:
            match = re.match(r'.*\$(\w+).*', path)
            if match is not None and match.group(1) is not None:
                all_envs[match.group(1)] = None

        for env in all_envs.iterkeys():
            if env not in os.environ:
                logger.critical("Could not find $%s envrionment variable!", env)
                is_ok = False

        assert is_ok

    def verify_if_files_exist_in_srcroot_paths(self, files):
        """
        Verify:s if files exists one way or another in the src-root-paths.
        Args:
            files(list): the list of files to verify
        Returns:
            found_files(list): list of files that is found inside include-paths, and not excluded.
        Raises:
            None
            Exits application if file does not seem to physically exist
        """
        local_files = []
        # First validation on absolute paths and that file do exist within the SRC_PATH
        for file_ in files:
            is_exists = False
            do_skip = False

            # First check if file contains any of the src-root-path exclude entrys
            for path in self._srcroots_exclude:
                if path in file_:
                    logger.critical("Skipping %s since it resides within exclude path %s", file_, path)
                    do_skip = True
                    break

            if do_skip:
                continue

            # First check if file contains any of the src-root-path include entrys
            for path in self._srcroots_include:
                if path in file_ and os.path.exists(file_):
                    is_exists = True
                    break

            if not is_exists:
                logger.critical("%s does not seem to exist!", file_)
                exit(1)

            local_files.append(file_)
        return local_files

    def find_all_files_in_srcroots(self, max_number_of_files=None):
        """
        Finds all files within the folders and files defined by the src-root-file
        Args:
            None
        Returns:
            files(list): sorted list of all files
        Raises:
            None
        """
        all_files = []
        for path in self._srcroots_include:
            logger.debug("searching path:%s", path)

            files = self._get_all_files_in_path(path, max_number_of_files)
            files.sort()  # a little bit more efficient than sorted()
            all_files.extend(files)
            if max_number_of_files is not None and len(all_files) >= max_number_of_files:
                break
        return all_files

    def _get_all_files_in_path(self, path, max_number_of_files=None):
        all_files = []
        for root, _, files in os.walk(path):
            for file_ in files:
                file_ = os.path.join(root, file_)
                do_add = True
                for excl_path in self._srcroots_exclude:
                    if excl_path in root or fnmatch(file_, excl_path):
                        do_add = False
                        break

                if do_add:
                    all_files.append(file_)
                    if max_number_of_files is not None and len(all_files) >= max_number_of_files:
                        return all_files
        return all_files

    def translate_env(self, path):
        '''
        Takes an absolute path and tries to transform it into a known path with env variables in it
        '''
        return self._env_parser.translate_to_env(path)
