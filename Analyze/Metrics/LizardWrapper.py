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
  This class wraps lizard, adding support for symbolic file translation
'''
import os

import lizard

from Utils import logger

class _SymbolicFileAnalyzer(lizard.FileAnalyzer):
    def analyze_file(self, file_, file_content=None):
        '''
        Lets lizard analyze if there exists a valid reader, otherwise it returns None

        lizard defaults to CLikeReader if no reader is found, to avoid this we explicitly
        check if a reader is found before calling
        '''
        if lizard.CodeReader.get_reader(file_) is not None:
            if file_content is None:
                with open(file_, 'rU') as f:
                    file_content = f.read()

            return self.analyze_source_code(file_, file_content)

class LizardIndexer(object):
    '''
    Indexes a file using lizard.
    This basically means that we analyze a file, building a database of where functions start and end.
    A user can then query the indexer for which function scope we are in based on a line number.
    '''
    @staticmethod
    def is_analyzable(file_):
        '''
        Checks if file_ is analyzable by lizard.
        Excluding python is due to a bug in lizard where some of our functions are not scoped correctly
        Somehow leading to a integrity error in the database.
        '''
        if lizard.CodeReader.get_reader(file_) is not None and not file_.endswith('.py'):
            return True
        else:
            return False

    def __init__(self, file_, filecontent=None, symbolic_filename_translator=lambda file_: file_):
        self._file = file_

        if filecontent is None:
            self._lizard_data = run_lizard(symbolic_filename_translator(self._file))
            with open(self._file) as f:
                self._total_lines = len(f.readlines())
        else:
            self._lizard_data = run_lizard(file_, filecontent)
            self._total_lines = len(filecontent.splitlines())

        self._function_lines = sum([func['end_line'] - func['start_line'] + 1 for func in self._lizard_data])

    def get_function_by_linenr(self, linenr, verbose=False):
        '''
        This function should output number-of-lines-of-code and not sloc, so we need to translate
        '''
        verbose = verbose
        for func in self._lizard_data:
            if linenr >= func['start_line'] and linenr <= func['end_line']:
                return func['name'], func['end_line'] - func['start_line'] + 1

        return '', self._total_lines - self._function_lines

def run_lizard(filename, filecontent=None):
    '''
    Runs lizard with the possibility of using a symbolic file translation
    Explanation of terms:
    'nloc': non-commented lines of code (commonly known as source-line-of-code)
            Note that this is NOT the same definition as used everywhere else in the maintainer_scripts
            where nloc means number-of-lines-of-code (i.e every single line, regardless of being comments or not).
    'token_count': Number of tokens (number of words)
    'parameter_count': Number of arguments passed to function

    Args:
            filename(str):                 The file to be analyzed, if filecontent != None, file will be read.
            filecontent(str):              If not None, this str will be used for analysis instead
    Returns:
            functions[dict]:                  All functions, including global scope (empty string)
                'name'(str)':                 function name (global scope is called "")
                'nloc'(int)':                 nloc for function
                'cyclomatic_complexity(int)': mccabes cyclomatic complexity
                'token_count'(int)':          #tokens in function
                'parameter_count'(int)':      #parematers passed to function
                'start_line'(int):            starting linenumber of function
                'end_line'(int):              ending linenumber of function

            If parsing fails an empty list will be returned
    '''
    lizard_object = _SymbolicFileAnalyzer(extensions=lizard.get_extensions([])).analyze_file(filename, filecontent)

    if lizard_object:
        function_list = [func.__dict__ for func in lizard_object.function_list]

        global_scope = {'name': '',
                        'nloc': lizard_object.nloc - sum([func.nloc for func in lizard_object.function_list]),
                        'cyclomatic_complexity': 0,
                        'token_count': 0,
                        'parameter_count': 0,
                        'start_line': 0,
                        'end_line': 0}

        function_list.insert(0, global_scope)

        logger.debug("Parsed file %s ", os.path.basename(filename))

        return function_list

    else:
        logger.debug("Unable to parse file %s", os.path.basename(filename))
        return []
