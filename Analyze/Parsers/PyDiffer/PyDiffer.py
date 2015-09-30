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
import sys
import argparse
import cPickle as pickle
import difflib
import re
import os

import __init__  # pylint: disable=W0611
from Utils import logger
from Utils import sysutils
from Utils.ProjectConfig import ProjectConfig, default_config

from Analyze.Metrics.LizardWrapper import LizardIndexer

class PyDiffer(object):
    '''
    Diffs 2 files, using fitting indexer and reports on their diff stats
    '''
    def __init__(self, file1, file2, symbolic_filename_translator=lambda file_: file_, config='test'):
        self._file1 = file1
        self._file2 = file2
        self._transformer_dictionary = {}
        if isinstance(config, ProjectConfig):
            self._transformer_dictionary = config.getdict('Analyze', 'code_transformer', {})  # pylint: disable=E1101

        self._symbolic_filename_translator = symbolic_filename_translator

    def _get_indexer(self, file_):
        content = []
        indexer = IndexerStub(file_)

        if file_ is not None:
            fileext_ = os.path.splitext(self._symbolic_filename_translator(file_))[1]
            transformer = self._transformer_dictionary.get(fileext_, None)
            if transformer is not None:
                mockfile = sysutils.call_subprocess(transformer.split() + [file_])
                indexer = LizardIndexer('mock.cpp', filecontent=mockfile)
                content = mockfile.splitlines()

            elif LizardIndexer.is_analyzable(self._symbolic_filename_translator(file_)):
                indexer = LizardIndexer(file_, symbolic_filename_translator=self._symbolic_filename_translator)
                with open(file_) as f:
                    content = f.readlines()
            else:
                with open(file_) as f:
                    content = f.readlines()

        return indexer, content

    def get_changestat(self):
        '''
        Performs diff between file1 & file2 and then collects statistics from the diff

        Returns:
            functions(dict): (added, changed, deleted, total)
                             A dictionary with function name as key and tuple of added, changed, deleted,
                             total #_total_lines per that function.
                             Global scope is indicated by an empty string = "" and includes everything not defined
                             as a function.
        '''
        return self._unified_diff()

    def _unified_diff(self):
        functions = {}
        re_control = re.compile(r"^@@ -(.*) \+(.*) @@")

        lh_index, lh_content = self._get_indexer(self._file1)
        rh_index, rh_content = self._get_indexer(self._file2)

        lines = list(difflib.unified_diff(lh_content, rh_content, n=0))

        cursor = 0
        while cursor < len(lines):
            line = lines[cursor].strip()
            cursor += 1
            if line.startswith(('+++', '---')):
                continue

            '''
            Consume range-info together with corresponding chunk
            range-info format is:
            @@ -l,s +l,s @@ optional section heading
            - => range-info is for left-hand file
            + => range-info is for right-hand file
            l => is the starting line number
            s => is the number of _total_lines the change hunk applies
            ,s => is optional, and if omitted number-of-_total_lines defaults to 1.
            '''
            match = re_control.match(line)
            if match is not None:
                lh = match.group(1).split(',')
                rh = match.group(2).split(',')

                lh_start = int(lh[0])
                if len(lh) <= 1:
                    lh_range = 1
                else:
                    lh_range = int(lh[1])

                rh_start = int(rh[0])
                if len(rh) <= 1:
                    rh_range = 1
                else:
                    rh_range = int(rh[1])

                cursor, diffchunk = self._consume_chunk(lines, cursor)
                diffcursor = 0

                # if len(diffchunk) <= 0, we can assume that entire diffchunk have been filtered out due
                # to ignore_attributes, so therefore we skip this chunk
                if len(diffchunk) <= 0:
                    continue

                if lh_range == rh_range:
                    '''
                    If ranges are equal, assume that entire diffchunk are line-by-line changes
                    '''
                    for index in range(0, rh_range):
                        linenr = rh_start + index
                        # Use rh func names, due to that if there was a rename, diff should be reported on the new name
                        func, total_ = rh_index.get_function_by_linenr(linenr)

                        try:
                            (added, changed, deleted, total) = functions[func]
                        except KeyError:
                            added, changed, deleted, total = 0, 0, 0, 0
                        changed += 1
                        functions[func] = (added, changed, deleted, total_)
                else:
                    while diffcursor < len(diffchunk):
                        op, line = diffchunk[diffcursor]
                        diffcursor += 1
                        added_, changed_, deleted_ = 0, 0, 0
                        if lh_range != 0:
                            # Only left-hand changes
                            linenr = lh_start + diffcursor - 1
                            func, _ = lh_index.get_function_by_linenr(linenr)
                            if op == '-':
                                deleted_ += 1
                            elif op == '+':
                                added_ += 1

                        elif rh_range != 0:
                            # Only right-hand changes
                            linenr = rh_start + diffcursor - 1
                            func, _ = rh_index.get_function_by_linenr(linenr)
                            if op == '-':
                                deleted_ += 1
                            elif op == '+':
                                added_ += 1

                        else:
                            logger.warning("strange range combo:%s at line:%s", match.group(0), diffcursor)
                            exit(-1)

                        try:
                            (added, changed, deleted, total) = functions[func]
                        except KeyError:
                            added, changed, deleted, total = 0, 0, 0, 0

                        added += added_
                        changed += changed_
                        deleted += deleted_

                        # Use rh to calculate function total length, since that is the "new" total.
                        rh_func, total = rh_index.get_function_by_linenr(linenr)

                        # if we could not find func in rh side, that means that function got deleted, and thus should
                        # have size=0, otherwise we report size of random function (or likely global scope)
                        if rh_func != func:
                            total = 0

                        functions[func] = (added, changed, deleted, total)
        return functions

    def _consume_chunk(self, lines, cursor):
        diffchunk = []
        while cursor < len(lines):
            line = lines[cursor].strip()
            if line.startswith("@@"):
                return cursor, diffchunk
            else:
                diffchunk.append((line[:1], line[1:]))
                cursor += 1
        return cursor, diffchunk

    def _get_filecontent(self, file_):
        with open(file_) as f:
            return f.readlines()


class IndexerStub(object):
    '''
    A file indexer that works on any file.
    But all lines are assumed to belong to global scope
    '''
    def __init__(self, file_):
        if file_ == "/dev/null":
            file_ = None
        self._file = file_
        self._total_lines = 0
        if file_ is not None:
            with open(file_) as f:
                for self._total_lines, _ in enumerate(f):
                    pass
            if self._total_lines != 0:
                self._total_lines += 1

    def get_function_by_linenr(self, line_number):
        '''
        Gets the function name for a specific line number
        But since this is a stub, it will assume global scope (empty string as name) for any line number

        Args:
            line_number(int): The line number to get the function for
        Returns:
            tuple(function_name, nloc_of_function)
        '''
        line_number = line_number
        return "", self._total_lines


def _main():
    main_help = """Diffs 2 files, if no arguments but the files are supplied then it
    fallbacks to context aware diff and outputs to a pickled stream"""
    parser = argparse.ArgumentParser(description=main_help)
    parser.add_argument('files', type=str, nargs=2, help="You must supply 2 files to perform diff on")
    help_ = "Makes the printout pretty instead of a pickle stream"
    parser.add_argument('-p', dest='pretty', action='store_true', help=help_)
    parser.add_argument('--config', dest='config', default=default_config, help="config file")
    parser.add_argument('-v', dest='verbose', action='store_true', help="Enable verbose mode")
    args = parser.parse_args()

    logger.setup_stdout_logger(args.verbose)

    stats = PyDiffer(args.files[0], args.files[1], config=ProjectConfig(args.config)).get_changestat()

    if args.pretty:
        # Find longest function name
        length = 0
        for func in stats.iterkeys():
            if len(func) > length:
                length = len(func)

        # Then print with formating adapted for the longest function name
        for func, (added, changed, deleted, total) in stats.iteritems():
            func_format = '{: <' + str(length + 3) + '}'
            func_format += func_format.format(func)
            func_format += '{: <10}'.format("total:" + str(total))
            func_format += '{: <10}'.format("added:" + str(added))
            func_format += '{: <10}'.format("changed:" + str(changed))
            func_format += '{: <10}'.format("deleted:" + str(deleted))
            print func_format
    else:
        pickle.dump(stats, sys.stdout, protocol=2)

if __name__ == '__main__':
    _main()
