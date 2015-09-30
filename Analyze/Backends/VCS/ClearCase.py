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
import subprocess
from datetime import datetime
import os
import re

from VcsWrapperContract import VcsWrapperContract
from Utils import sysutils
from Analyze.Parsers.PyDiffer import PyDiffer


def _is_checkin_history_element(item):
    return item['action'] in 'checkin' and \
           not item['activity'].startswith("deliver.") and \
           not item['activity'].startswith("rebase.")


class ClearCase(VcsWrapperContract):
    '''
    Class for handling ClearCase interaction
    '''
    def __init__(self, config, cleartool='cleartool', **kwargs):
        """
        Args:
            config (ProjectConfig): instance of project config, should contain a ClearCase section
            cleartool(str): path-to-cleartool, defaults to "cleartool".
        Returns:
            None
        Raises:
            None
        """
        kwargs = kwargs
        super(ClearCase, self).__init__()
        self._path_to_clearcase = config.get('ClearCase', 'path_to_cleartool', cleartool)

        '''
        Defect regex config evaluation
        '''
        self._defect_regexp_all = config.get('General', 'defect_modification_regexp_all', None)
        self._defect_regexp_all_c = None
        if self._defect_regexp_all is not None:
            self._defect_regexp_all_c = re.compile(self._defect_regexp_all)

        self._lsv_branches = config.getlist('General', 'lsv_branches')

    def find_contributors(self, file_, since_date=None):
        """
        Finds and sorts all contributors (anyone who has done any checkin operations in any branch on file_)

        Args:
            file_(str): The file to lookup contributors on
            since_date(datetime): Only lookup checkin operations from today to since_date,
                                 If None, since_date is assumed to be today-(3 years).
        Returns:
            sorted_entries(list), total_entries(int): sorted_entries is a list of tuples (name, nCheckins, email),
                                                    total_entries is the total number of checkins during that period
        Raises:
            None
        """
        not_delivered_or_rebased_entries = self._find_contributions(file_, since_date)

        ackumulated_entries = {}
        for entry in not_delivered_or_rebased_entries:
            if entry['user'] not in ackumulated_entries:
                ackumulated_entries[entry['user']] = 1
            else:
                ackumulated_entries[entry['user']] += 1

        sorted_entries = sorted(ackumulated_entries.iteritems(), key=lambda (k, v): (v, k), reverse=True)
        return sorted_entries, len(not_delivered_or_rebased_entries)

    def find_all_defects(self, file_, since_date=None, changeinfo=False):
        """
        Finds all defects for file_, this is achieved by:
        git:
        Parsing status line (or Activity tag) matching something in the line of GGSNxxxxxx or trXXXXX.
        CC:
        Parsing branchname looking for name matching something in the line of GGSNxxxxxx or trXXXXX.

        Args:
            file_(str): The file to lookup defects on
            since_date(datetime): Only return defect commits created since since_date
            changeinfo(bool): If enabled, performs diff for each defect including changed-function metrics
        Returns:
            dict(defect_id): entry['user'](str) : creator of commit
                             entry['datetime'](datetime) : creation time of commit
                             entry['version'](str) : git=commit hash, CC=elem version
                             entry['functions'](list[str]) : list of functions (changed classes/functions)
                                                             only available if changeinfo=True
                             entry['diffchunks'] : list of ndiff formated diffchunks (details TBD)
                                                            only available if changeinfo=True
        Raises:
            None
        """
        defect_mods = {}
        if changeinfo:
            defect_mods = self._match_branches_to_defects(self._get_history(file_, since_date),
                                                          lambda(x): x['version'],
                                                          lambda(x): x['activity'])

            # Remove defect branches that never got delivered
            defect_mods = {k: v for (k, v) in defect_mods.iteritems() for elem in v if elem['merge-to'] != ""}

            for defect_id, entries in defect_mods.iteritems():
                '''
                This is a really ugly setup with the getDelivered thingy, but dont have time to clean
                it out and CC is on the decline anyway
                '''
                for elem, delivered_elem, rebased_elem in self._get_delivered_and_rebased_elems(file_, entries):
                    entry = {}
                    entry.update(elem)
                    entry.update(self._get_changed_functions(rebased_elem, delivered_elem))
                    defect_mods.setdefault(defect_id, []).append(entry)
        else:
            '''
            This unfortunatly also includes branches that may not have been delivered, but is faster
            than doing the detailed query using describe above
            '''
            defect_mods = self._match_branches_to_defects(self._get_branch_names(file_),
                                                          lambda(x): x,
                                                          lambda(x): x)
        return defect_mods

    def symbolic_filename_translator(self, file_):
        '''
        Translates the symbolic filename as known by clearcase into a more human readable filename
        '''
        return file_.split("@@")[0]

    def get_lsv_versions(self, file_, since_date=None, regexstr=None):
        """
        Gets all (LSV, Latest-System-Version) version strings for a file.
        CC: version-string = element version
        git: commit hash

        Args:
            file_(str): The file to get the LSV version strings for
            since_date(datetime): Only get versions created since since_date
        Returns:
            versions(list): A descending sorted list of all versions defined as:
                                        entry['version'](str): file element id (CC = elemid, git = commit hash)
                                        entry['datetime'](datetime): creation date for element
                                        entry['user'](str): user who created element
                                        ---- CC specific ----
                                        entry['activity'](str): UCM activity attached to the version
        Raises:
            None
        """
        regexstr = regexstr
        versions = []

        # First get info for all versions on all lsv branches
        all_branches = self._get_branch_names(file_)
        for branch_to_find in self._lsv_branches:
            abs_branch = None
            for absolute_branchname in all_branches.iterkeys():
                if absolute_branchname.endswith(branch_to_find):
                    abs_branch = absolute_branchname
                    break
            if abs_branch is not None:
                for versionpath in self._get_branch_history(file_, abs_branch):
                    element = {}
                    element['version'] = versionpath
                    element.update(self._describe_element(self.checkout_file_version(file_, versionpath)))
                    versions.append(element)

        return sorted(versions, key=lambda(version): version['datetime'])

    def checkout_file_version(self, file_, version):
        """
        Gets the file path for a file matching version

        Args:
            file_(str): The file to get the version for
            version(str): The version string (as returned from get_lsv_versions() to get the filepath for
        Returns:
            filepath(str)
        Raises:
            None
        """
        return file_ + "@@" + version

    def update_repo(self):
        """
        Updates view to the stream config-spec.
        i.e, calls:
        $>cleartool setcs --stream

        Raises:
            None
        Returns:
            (Boolean): True if update succeeded, otherwise False
        """
        rc, _ = sysutils.call_subprocess([self._path_to_clearcase, 'setcs', '--stream'], with_errno=True)
        if rc is 0:
            return True
        else:
            return False

    def checkout_repo_version(self, version):
        """
        Checkouts the entire repo to a specific version
        The reason for why we would want to do this is due to that some files have strong dependencies between
        themselves that we must take into consideration (for instance dependency between a rhapsody component and
        its scoped models) So by checking out the entire repo we can make sure that the intra-file dependency
        is consistent.

        To reset repo to whatever branch it was viewing previously you must call uncheckout_repo_version().

        Args:
            version(str): The version string (as returned from get_lsv_versions())
        Returns:
            None
        Raises:
            None
        """
        raise NotImplementedError("This has not yet been implemented for ClearCase")

    def uncheckout_file_version(self, tmp_file):
        """
        This cleans out everything that might have been created by checkout_file_version()

        Since checkout_file_version is more or less a no-op in CC, there is nothing to clean out.
        Raises:
            None
        """
        pass

    def uncheckout_repo_version(self):
        """
        This resets the repo version to whatever it was prior to checkoutRepoVerison was called.

        Raises:
            None
        """
        raise NotImplementedError("This has not yet been implemented for ClearCase")

    def _find_contributions(self, file_, since_date=None):
        """
        Finds all contributions (checkins, not deliver or rebase)

        Args:
            file_(str): The file to lookup contributions on
            since_date(datetime): Only lookup checkin operations from today to since_date,
                                 If None, since_date is assumed to be today-(3 years).
        Returns:
            contributions(list): entry(dict): keys=datetime, name, action, version

        Raises:
            None
        """
        history_entries = [his for his in self._get_history(file_, since_date) if _is_checkin_history_element(his)]
        return history_entries

    def _get_delivered_and_rebased_elems(self, file_, elements_on_defect_branch):
        # find deliveries
        sorted_elems = sorted(elements_on_defect_branch, key=lambda(elem): elem['version'])
        delivery_and_rebase_elems = []
        for index, elem in enumerate(sorted_elems):
            if elem['merge-to'] != "":
                delivered_elem = self.checkout_file_version(file_, elem['version'])
                # find latest previous rebase
                for i in range(index, -1, -1):
                    if sorted_elems[i]['merge-from'] != "":
                        rebased_elem = sorted_elems[i]['merge-from']
                        break
                    elif i == 0:
                        rebased_elem = self.checkout_file_version(file_, sorted_elems[i]['version'])
                        # Is a bit dangerous, if a user has named his branch as a string of digits
                        # Could perhaps be improved if one added to lshistory to only print real file elements
                        if os.path.basename(rebased_elem).isdigit() is False:
                            rebased_elem = rebased_elem + "/0"
                        break

                delivery_and_rebase_elems.append((elem, delivered_elem, rebased_elem))
        return delivery_and_rebase_elems

    def _get_changed_functions(self, element1, element2):
        """
        Executes gnu diff on elements to get the number of lines added/changed/deleted

        Args:
            element1(str): the full path to the element version (gsc.c@@/main/1)
            element2(str): the full path to the element version (gsc.c@@/main/2)
        Returns:
            dict{}:
                dict['functions'](str) : Changed functions/function
        Raises:
            None
        """
        diffEntry = {}
        if element1 is None:
            element1 = "/dev/null"
        if element2 is None:
            element2 = "/dev/null"

        diffs = PyDiffer.PyDiffer(element1,
                                  element2,
                                  symbolic_filename_translator=self.symbolic_filename_translator).get_changestat()
        diffEntry['functions'] = list(diffs.iterkeys())

        return diffEntry

    def _match_branches_to_defects(self, list_of_elements, find_branch_name, random_identifier):
        matching_branches = {}
        for branch_entry in list_of_elements:
            match = self._defect_regexp_all_c.search(find_branch_name(branch_entry))
            if match is not None:
                if self._defect_regexp_all_c.groups <= 0:
                    matching_branches.setdefault(random_identifier(branch_entry),
                                                 []).append(find_branch_name(branch_entry))
                else:
                    defect_ids = [id_.lstrip('0') for id_ in match.groups() if id_ is not None]
                    if len(defect_ids) > 0:
                        # Make sure that all captured groups are identical
                        assert defect_ids.count(defect_ids[0]) == len(defect_ids)
                        matching_branches.setdefault(defect_ids[0], []).append(find_branch_name(branch_entry))

        return matching_branches

    def _get_branch_names(self, file_):
        """
        Executes cleartool lsvtree on file_ to get the branch history
        Then returns a dictionary of all branchnames

        Args:
            file_: The file to get the branchnames for
        Returns:
            branch_entries(dict): A dictionary with branchname as key and number of elements as value
        Raises:
            None
        """
        branch_entries = {}
        output = ""

        try:
            output = subprocess.check_output([self._path_to_clearcase, "lsvtree", "-short", "-obs", file_],
                                             stderr=open(os.devnull, 'w')).splitlines()
        except subprocess.CalledProcessError:
            pass

        for line in output:
            entry_line = line.split('@@')
            branch_name, _ = os.path.split(entry_line[1].strip())
            if branch_name not in branch_entries:
                branch_entries[branch_name] = 1
            else:
                branch_entries[branch_name] += 1

        return branch_entries

    def _get_history(self, file_, since_date):
        """
        TBD: update doc header
        Executes cleartool lshistory on file_ to get a list of all activites (not UCM act) on that file
        Then returns a list of all activites (containing dicts with [datetime, name, action] keys)

        Args:
            file_: The file to get the element history for
        Returns:
            history_entries(list): A list of all activites (containing dicts with [datetime, name, action] keys)
        Raises:
            None
        """
        history_entries = []
        output = ""

        # ct lshistory -fmt %d\\t%u\\t%o\\t%[activity]p\\t%Vn\\t%[hlink]Hp\\n gsc/gsc_etfctrl.c
        format_ = "%d\\t%u\\t%o\\t%[activity]p\\t%Vn\\t%[hlink]p\\n"
        if since_date is not None:
            since_arg1 = "-since"
            since_arg2 = since_date.strftime("%Y-%m-%d")
            caller = [self._path_to_clearcase, "lshistory", since_arg1, since_arg2, "-fmt", format_, file_]
        else:
            caller = [self._path_to_clearcase, "lshistory", "-fmt", format_, file_]

        try:
            output = subprocess.check_output(caller, stderr=open(os.devnull, 'w')).splitlines()
        except subprocess.CalledProcessError:
            pass

        for line in output:
            history_entry = {}

            entry_line = line.split('\t')
            '''2013-04-24T17:11:07+02:00
               tzinfo (%z) is not supported in strptime, so ignore it for now
               (could be solved by manually parsing it)'''
            history_entry['datetime'] = datetime.strptime(entry_line[0][:-6], '%Y-%m-%dT%H:%M:%S')
            history_entry['user'] = entry_line[1].strip()
            history_entry['action'] = entry_line[2].strip()
            history_entry['activity'] = entry_line[3].strip()
            history_entry['version'] = entry_line[4].strip()
            history_entry['merge-from'] = ""
            history_entry['merge-to'] = ""

            try:
                merges = entry_line[5].strip().split(' ')
            except IndexError:
                pass

            for index, element in enumerate(merges):
                if element == '->':
                    history_entry['merge-to'] = merges[index + 1].strip(' \"')
                elif element == '<-':
                    history_entry['merge-from'] = merges[index + 1].strip(' \"')

            history_entries.append(history_entry)

        return history_entries

    def _get_branch_history(self, file_, branch):
        """
        Executes cleartool lshistory on branch to get a list of all elements for that branch
        Args:
            file(str): The file to get the branches element names on
            branch(str): The branch to get the elements
        Returns:
            versionpaths[str]: A list of strings with version paths

        Raises:
            None
        """

        versionpaths = []
        output = ""
        try:
            '''ct lsvtree -nrec -branch /main/mpg_mainline_int/mpg_lsv_int -obsolete gsc/gsc_boardhandler.h'''
            output = subprocess.check_output([self._path_to_clearcase, "lsvtree",
                                              "-short", "-nrec", "-obsolete", "-branch", branch, file_],
                                             stderr=open(os.devnull, 'w')).splitlines()
        except subprocess.CalledProcessError:
            pass

        for line in output:
            if os.path.isfile(line):
                entry_line = line.split('@@')
                versionpaths.append(entry_line[1].strip())
        return versionpaths

    def _describe_branch(self, branch):
        """
        Executes wstool describe on branch to get the creater name and date for it

        Args:
            file_: The file to get the branch description on
        Returns:
            descriptionEntry(dict): Dictionary with [datetime, name] keys
        Raises:
            None
        """
        format_ = "%d\\t%u\\n"
        desc_entry = {}
        output = ""
        try:
            output = subprocess.check_output([self._path_to_clearcase, "desc", "-fmt", format_, branch],
                                             stderr=open(os.devnull, 'w')).splitlines()
        except subprocess.CalledProcessError:
            pass

        for line in output:
            entry_line = line.split('\t')
            '''2013-04-24T17:11:07+02:00
               tzinfo (%z) is not supported in strptime, so ignore it for now
               (could be solved by manually parsing it)'''

            desc_entry['datetime'] = datetime.strptime(entry_line[0][:-6], '%Y-%m-%dT%H:%M:%S')
            desc_entry['user'] = entry_line[1].strip()
            # Assumes that there is only 1 desc entry for one branch
            return desc_entry

        return desc_entry

    def _describe_element(self, element):
        """
        Executes cleartool describe on element to get the creater name,date,activity for it

        Args:
            element(str): the full path to the element version (gsc.c@@/main/1
        Returns:
            descriptionEntry(dict): Dictionary with [datetime, user, activity] keys
        Raises:
            None
        """
        format_ = "%d\\t%u\\t%[activity]p\\n"
        desc_entry = {'datetime': None, 'user': None, 'activity': None, }
        output = ""
        try:
            output = subprocess.check_output([self._path_to_clearcase, "desc", "-fmt", format_, element],
                                             stderr=open(os.devnull, 'w')).splitlines()
        except subprocess.CalledProcessError:
            pass

        for line in output:
            entry_line = line.split('\t')
            desc_entry['datetime'] = datetime.strptime(entry_line[0][:-6], '%Y-%m-%dT%H:%M:%S')
            desc_entry['user'] = entry_line[1].strip()
            desc_entry['activity'] = entry_line[2].strip()
            # Assumes that there is only 1 desc entry for one element
            return desc_entry

        return desc_entry
