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
  Counts changerate between versions
'''
import os

from Analyze.Parsers.PyDiffer import PyDiffer


class ChangeRate(object):
    '''
    Counts changerate
    Basically the added, changed, deleted LOC between versions
    '''
    def __init__(self, vcs):
        self._vcs = vcs

    def count_change_rate(self, prev_version, curr_version):
        '''
        Counts the changerate between prev_version and curr_version.
        Returns:
            functions(dict): (added, changed, deleted, total)
                             A dictionary with function name as key and tuple of added, changed, deleted, total
                              #_total_lines per that function.
                             Global scope is indicated by an empty string = "" and includes everything not defined
                             as a function.
        '''
        return PyDiffer.PyDiffer(prev_version, curr_version,
                                 symbolic_filename_translator=self._vcs.symbolic_filename_translator).get_changestat()

    def count_change_rate_all(self, file_, since_date=None):
        """
        Counts the changerate for file_, this is calculated by performing a diff between each version on all
        LSV branches. It then returns a list of all element versions and their diffs.

        Args:
            file_: The file to get the LSV changerate for
            since_date(datetime): Only count changerate for versions created since since_date
        Returns:
            elements(list): A list of all elements defined as:
                                        entry['version'](str): file element id (CC = elemid, git = commit hash)
                                        entry['datetime'](datetime): creation date for element
                                        entry['user'](str): user who created element
                                        entry['changerate'](dict): function: (added,changed, deleted, total)
                                        ---- git specific elements ----
                                        entry['email'](str): email of user
                                        entry['subject'](str): subject of commit
                                        entry['is_root'](bool): Indicating that this is the first version in the tree
        """
        elements = self._vcs.get_lsv_versions(file_, since_date)

        # Count changerate between each element
        for index, element in enumerate(elements):
            element['changerates'] = {}
            curr_version = self._vcs.checkout_file_version(file_, element['version'])
            if os.path.isfile(curr_version):
                if (index - 1) >= 0:  # Not root version
                    prev_version = self._vcs.checkout_file_version(file_, elements[index - 1]['version'])
                    if os.path.isfile(prev_version):
                        element['changerates'] = self.count_change_rate(prev_version, curr_version)
                        self._vcs.uncheckout_file_version(prev_version)
                else:  # is root version
                    element['changerates'] = self.count_change_rate(None, curr_version)

                self._vcs.uncheckout_file_version(curr_version)
        return elements
