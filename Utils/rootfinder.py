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
  Simple convinience script for finding root folder of the repo.
  Typically, create a symlink __init__.py -> Utils/rootfinder.py, and as soon as that package is imported, this
  file will make sure that the root path is in sys.path.
  If you want to add custom things into your init, instead of creating a symlink make sure to import this file from
  that custom __init__, and it will still be able to set up sys.path
'''

import os
import sys


def find_repo_rootdir():
    '''
    Finds the repo:s rootdir by looking for the marker file .THIS_IS_ROOT
    It then returns the absolute path to the repo root
    '''
    def __check_parent(topdir):
        for _, _, files in os.walk(topdir):
            if '.THIS_IS_ROOT' in files:
                return topdir
            else:
                next_ = topdir.rsplit("/", 1)
                if len(next_) == 2:
                    return __check_parent(next_[0])
                else:
                    return None
    return __check_parent(os.path.abspath(os.path.dirname(__file__)))

repo_root = find_repo_rootdir()
if repo_root is not None and repo_root not in sys.path:
    sys.path.append(repo_root)
