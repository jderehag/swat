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
import os
import sys
import subprocess
ignore_folders = ['.git',
                  os.path.join('www', 'MetricsViewer', 'visualization', 'static', 'visualization', 'node_modules')]
ignore_files = []

def check_pylint(file_):
    '''
    Executes pylint on file_
    Args:
        file_(str): File to execute pylint on
    Returns:
        rc(int): Return code for pylint
    '''
    rcfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylintrc")
    return subprocess.call('pylint --rcfile="{}" -f text -r n "{}"'.format(rcfile, file_), shell=True)

def is_valid_file(file_):
    '''
    Checks wether file should be checked or ignored
    Args:
        file_(str): File to execute pylint on
    Returns:
        valid(Boolean): True if file should be checked
    '''
    if not os.path.isfile(file_):
        print file_, "is not a file!"
        return False

    for ignore_folder in ignore_folders:
        if ignore_folder in file_:
            return False

    if os.path.basename(file_) in ignore_files:
        return False

    return True


def find_all_valid_files():
    '''
    Traverses repo from rootdir and finds all valid files to be checked

    Returns:
        files(list): List of all valid files
    '''
    files_to_test = []
    rootdir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
    for dirpath, _, files in os.walk(rootdir):
        for file_ in files:
            abspath = os.path.join(dirpath, file_)
            if is_valid_file(abspath):
                files_to_test.append(abspath)
    return files_to_test


def main():
    # pylint: disable=C0111
    if len(sys.argv) < 2:
        files = find_all_valid_files()
    else:
        files = [os.path.abspath(file_) for file_ in sys.argv[1:]]

    was_successful = True
    for file_ in files:
        if is_valid_file(file_) and file_.endswith('.py'):
            if check_pylint(file_) != 0:
                was_successful = False

    if not was_successful:
        print os.path.basename(__file__), "failed!"
        exit(1)

if __name__ == '__main__':
    main()
