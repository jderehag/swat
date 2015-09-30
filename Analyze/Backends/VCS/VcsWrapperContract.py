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
  VcsWrapperContract defines all methods that needs to be implemented by a VCS implementation (You need to inherit this
  class if you want to implement a VcsWrapped class)
'''


class VcsWrapperContract(object):
    '''
    A simple contract for which functions any VCS implementation *must* implement
    '''
    def find_contributors(self, file_, since_date=None):
        """
        Finds and sorts all contributors (anyone who has done any checkin operations in any branch on file_)

        Args:
            file_(str): The file to lookup contributors on
            since_date(datetime): Only lookup checkin operations from today to since_date,
                                 If None, since_date is assumed to be today-(3 years).
        Returns:
            sorted_entries(list), total_entries(int): sorted_entries is a list of tuples (name, nCheckins),
                                                    total_entries is the total number of checkins during that period
        Raises:
            None
        """
        raise NotImplementedError("A VCS implementation must implement this!")

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
            dict(trnumber): entry['user'](str) : creator of commit
                            entry['datetime'](datetime) : creation time of commit
                            entry['version'](str) : git=commit hash, CC=elem version
                            entry['functions'](list[str]) : list of functions (changed classes/functions)
                                                            only available if changeinfo=True
                            entry['diffchunks'] : list of ndiff formated diffchunks (details TBD)
                                                            only available if changeinfo=True
        Raises:
            None
        """
        raise NotImplementedError("A VCS implementation must implement this!")

    def get_lsv_versions(self, file_, since_date=None, regexstr=None):
        """
        Gets all (LSV) version strings for a file.
        CC: version-string = element version
        git: commit hash

        Args:
            file_(str): The file to get the LSV version strings for
            since_date(datetime): Only get versions created since since_date
        Returns:
            versions(list): A sorted list of all versions defined as:
                                        entry['version'](str): file element id (CC = elemid, git = commit hash)
                                        entry['datetime'](datetime): creation date for element
                                        entry['user'](str): user who created element
        Raises:
            None
        """
        raise NotImplementedError("A VCS implementation must implement this!")

    def update_repo(self):
        """
        Updates repo to latest version of set branch.
        CC: cleartool setcs --stream
        git: git pull origin master

        Raises:
            None
        Returns:
            (Boolean): True if update succeeded, otherwise False
        """
        raise NotImplementedError("A VCS implementation must implement this!")

    def checkout_file_version(self, file_, version):
        """
        Gets the file path for a file matching version

        CC:
        Returns the absolute path to a specific element-version
        git:
        Create a temporary file with the contents of file/version, then return the path to the temporary file.

        To make sure we have no leaking temporary files it is very important to call uncheckout_file_version() when
        you are done processing the temporary files.

        Args:
            file_(str): The file to get the version for
            version(str): The version string (as returned from get_lsv_versions() to get the filepath for
        Returns:
            filepath(str)
        Raises:
            None
        """
        raise NotImplementedError("A VCS implementation must implement this!")

    def checkout_repo_version(self, version):
        """
        Checkouts the entire repo to a specific version
        The reason for why we would want to do this is due to that some files have strong dependencies between
        themselves that we must take into consideration (for instance dependency between a rhapsody component and
        its scoped models) So by checking out the entire repo we can make sure that the intra-file dependency is
        consistent.

        To reset repo to whatever branch it was viewing previously you must call uncheckout_repo_version().

        Args:
            version(str): The version string (as returned from get_lsv_versions())
        Returns:
            None
        Raises:
            None
        """
        raise NotImplementedError("A VCS implementation must implement this!")

    def uncheckout_file_version(self, tmp_file):
        """
        This cleans out everything that might have been created by checkout_file_version()

        Raises:
            None
        """
        raise NotImplementedError("A VCS implementation must implement this!")

    def uncheckout_repo_version(self):
        """
        This resets the repo version to whatever it was prior to checkoutRepoVerison was called.

        Raises:
            None
        """
        raise NotImplementedError("A VCS implementation must implement this!")
