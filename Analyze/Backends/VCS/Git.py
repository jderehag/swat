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
from datetime import datetime
import os
import re
import pickle
import tempfile
import uuid

from VcsWrapperContract import VcsWrapperContract
from Utils import sysutils, logger
from Analyze.Parsers.PyDiffer import PyDiffer


class Git(VcsWrapperContract):
    '''
    Class for handling _git interaction
    '''
    # Pretty formating options in _git
    PF_commit_hash = "%H"
    PF_author_name = "%an"
    PF_author_email = "%ae"
    PF_author_date = "%ai"
    PF_subject = "%s"
    PF_body = "%b"

    def __init__(self, config, path_to_git='git', tmp_dir_prefix='swat_',
                 shared_dict_ctor=dict):
        super(Git, self).__init__()
        self._path_to_git = config.get('Git', 'path_to_git', path_to_git)
        self._is_branch_checkedout = False
        self._tmpfiles = []
        self._filealias_cache = shared_dict_ctor()

        self._repo = config.get('Git', 'repo_root')
        self._current_branch = self._git('rev-parse --abbrev-ref HEAD')

        self._ignore_users = config.getlist('General', 'ignore_elements_by_user')

        '''
        Defect regex config evaluation
        '''
        self._defect_regexp_all = config.get('General', 'defect_modification_regexp_all', None)
        self._defect_regexp_all_c = None
        self._defect_regexp_subject = config.get('General', 'defect_modification_regexp_subject', None)
        self._defect_regexp_subject_c = None
        self._defect_regexp_body = config.get('General', 'defect_modification_regexp_body', None)
        self._defect_regexp_body_c = None

        if self._defect_regexp_all is not None:
            self._defect_regexp_all_c = re.compile(self._defect_regexp_all)

        if self._defect_regexp_subject is not None:
            self._defect_regexp_subject_c = re.compile(self._defect_regexp_subject)

        if self._defect_regexp_body is not None:
            self._defect_regexp_body_c = re.compile(self._defect_regexp_body)

        '''
        tmpdir config
        '''
        self._tmpdir = os.path.join(tempfile.gettempdir(), tmp_dir_prefix + str(uuid.uuid4()))
        if not os.path.exists(self._tmpdir):
            os.makedirs(self._tmpdir)

    def __del__(self):
        self.uncheckout_file_version()
        self.uncheckout_repo_version()

    def _git(self, args, with_errno=False):
        if isinstance(args, str):
            args = args.split(' ')
        output = sysutils.call_subprocess([self._path_to_git] + args, with_errno=with_errno, cwd=self._repo)

        if with_errno:
            output = output[0], output[1].strip()
        else:
            output = output.strip()

        return output

    def find_contributors(self, file_, since_date=None):
        """
        Finds and sorts all contributors

        Args:
            file_(str): The file to lookup contributors on
            since_date(datetime): Only lookup contributions from today to since_date,
                                 If None, since_date is assumed to be today-(3 years).
        Returns:
            sorted_entries(list), total_entries(int): sorted_entries is a list of tuples (name, nCheckins),
                                                    total_entries is the total number of commits during that period
        Raises:
            None
        """

        contributions = self.get_lsv_versions(file_, since_date)

        ackumulated_entries = {}
        for entry in contributions:
            if entry['user'] not in self._ignore_users:
                if entry['user'] not in ackumulated_entries:
                    ackumulated_entries[entry['user']] = 1
                else:
                    ackumulated_entries[entry['user']] += 1

        sorted_entries = sorted(ackumulated_entries.iteritems(), key=lambda (k, v): (v, k), reverse=True)
        return sorted_entries, len(contributions)

    def find_all_defects(self, file_, since_date=None, changeinfo=False):
        """
        Finds all defects for file_, this is achieved by:
        _git:
        Parsing status line (or Activity tag) matching something in the line of GGSN----- or defect----.
        CC:
        Parsing branchname looking for name matching something in the line of GGSN----- or defect----.

        Args:
            file_(str): The file to lookup defects on
            since_date(datetime): Only return defect commits created since since_date
            changeinfo(bool): If enabled, performs diff for each defect including changed-function metrics
        Returns:
            dict(defect_ud): entry['version'](str): file element id (CC = elemid, _git = commit hash)
                             entry['datetime'](datetime): creation date for element
                             entry['user'](str): user who created element
                             entry['functions'](list[str]) : list of functions (changed classes/functions)
                                                            only available if changeinfo=True
                             ---- _git specific elements ----
                             entry['email'](str): email of user
                             entry['subject'](str): subject of commit
                             entry['is_root'](bool): Indicating that this is the first version in the tree
        Raises:
            None
        """
        defects = self._find_defects_in_commit_history(file_, since_date)
        if changeinfo:
            for defect_list in defects.itervalues():
                for defect in defect_list:
                    version = defect['version']
                    filealias = defect['filealias']

                    '''
                    This awkwardness is due to that in python2, __file__ points to the compiled file.
                    While, git can only accept a single binary as --extcmd, therefore its not possible to
                    do the "python PyDiffer.pyc" version of things. Instead we point directly to PyDiffer
                    relying on that the shell will correctly identify this as a python file (this may not work
                    in windows).
                    '''
                    pydiffer = PyDiffer.__file__
                    if pydiffer.endswith('c'):
                        pydiffer = pydiffer[:-1]

                    args = ['difftool', '-M',
                            '--extcmd="' + os.path.realpath(pydiffer) + '"']
                    args += [version + "^!", "--", filealias]
                    output = self._git(args)
                    try:
                        stats = pickle.loads(output)
                    except EOFError:
                        logger.critical("Cought EOFError from pickle when executing:%s", 'git ' + ' '.join(args))
                        defect['functions'] = []
                    else:
                        defect['functions'] = list(stats.iterkeys())
        return defects

    def get_lsv_versions(self, file_, since_date=None, regexstr=None):
        """
        Gets all (LSV) (i.e master) version strings for a file.
        CC: version-string = element version
        _git: commit hash

        Args:
            file_(str): The file to get the LSV version strings for
            since_date(datetime): Only get versions created since since_date
        Returns:
            versions(list): A sorted list of all versions defined as:
                                        entry['version'](str): file element id (CC = elemid, _git = commit hash)
                                        entry['datetime'](datetime): creation date for element
                                        entry['user'](str): user who created element
                                        ---- _git specific elements ----
                                        entry['email'](str): email of user
                                        entry['subject'](str): subject of commit
                                        entry['body'](str): body of commit
                                        entry['is_root'](bool): Indicating that this is the first version in the tree
                                        entry['filealias'](str): filename alias

        Raises:
            None
        """
        if regexstr is not None:
            '''
             --grep dont seem to work together with --follow
             We therefore read the entire body and do our own grep of the log
             caller.extend(["-E", "--grep=" + regexstr])
            '''
            regex = re.compile(regexstr)
        else:
            regex = None
        commit_identifier = str(uuid.uuid4())
        output_format = "--pretty=" + commit_identifier + \
                        "\t".join([Git.PF_author_date, Git.PF_author_name, Git.PF_commit_hash, Git.PF_author_email,
                                   Git.PF_subject]) + "$body$" + Git.PF_body + "$endbody$"

        args = 'log --follow --name-only ' + output_format

        if since_date is not None:
            args += " --since=\"" + since_date.strftime("%Y-%m-%d") + "\""

        args += ' -- ' + file_
        output = self._git(args)

        initial_commits = self._find_root_versions(file_)
        contributions = []
        for commit in output.split(commit_identifier):
            commit = commit.split('$body$')
            if len(commit) != 2:
                continue
            # This should really be cleaned up using better formating and regexp.
            header, tail = commit[0], commit[1]
            tail = tail.split('$endbody$')
            commit_body = tail[0]
            if len(tail) == 2:
                filealias = tail[1].strip()
            else:
                filealias = file_.strip()

            entryline = header.split('\t')

            '''2013-04-24 17:11:07 +0200
               tzinfo (%z) is not supported in strptime, so ignore it for now
               (could be solved by manually parsing it)'''
            commit_date = datetime.strptime(entryline[0][:-6], '%Y-%m-%d %H:%M:%S')
            commit_user = entryline[1].strip()
            commit_hash = entryline[2].strip()
            commit_email = entryline[3].strip()
            commit_subject = entryline[4].strip()
            if commit_hash in initial_commits:
                is_root = True
            else:
                is_root = False

            entry = {'datetime': commit_date,
                     'user': commit_user,
                     'version': commit_hash,
                     'email': commit_email,
                     'subject': commit_subject,
                     'body': commit_body,
                     'is_root': is_root,
                     'filealias': filealias}

            # All regexp matching is assumed to be on lower-case, therefore transform strings prior to search
            if regex is None or regex.search(commit_subject.lower() + commit_body.lower()) is not None:
                contributions.append(entry)
                # since filealias_cache *might* be a DictProxy, setdefault does not work
                filecache = self._filealias_cache.get(file_, {})
                filecache[commit_hash] = filealias
                self._filealias_cache[file_] = filecache

        return sorted(contributions, key=lambda(contribution): contribution['datetime'])

    def symbolic_filename_translator(self, file_):
        '''
        Translates the symbolic filename as known by VCS into a more human readable filename
        In git this is a noop
        '''
        return file_

    def update_repo(self):
        """
        Updates repo to latest version of set branch.
        i.e, calls:
        $>_git pull
        $>_git submodule update --init

        Raises:
            None
        Returns:
            (Boolean): True if update succeeded, otherwise False
        """
        logger.debug('Running git pull on %s',)
        acc_rc = 0
        rc, _ = self._git('pull --recurse-submodules=yes', with_errno=True)
        acc_rc = acc_rc | rc

        logger.debug('_git pull done...')

        rc, _ = self._git('submodule update --init', with_errno=True)
        acc_rc = acc_rc | rc

        if rc != 0:
            return False
        else:
            return True

    def checkout_file_version(self, file_, version):
        """
        Gets the file path for a file matching version

        What this means in the _git world is that we create a temporary file with the contents of file/version
        We then return the path to the temporary file.

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

        file_ = os.path.normpath(os.path.realpath(file_))
        filealias = self._get_filealias(file_, version)

        # _git show requires that the path to the file is relative to the repo top dir (no absolute paths)
        relfile = filealias.replace(self._get_repo_top_dir() + "/", "")
        output = self._git('show ' + version + ':' + relfile)

        '''
        This creates a physical tmp file which needs to be cleaned out at some point.
        To do that, we maintain a list of all temporary files and let either the user call uncheckout_file_version()
        to clean them all out, or they are cleaned out at the dtor for vcs class.
        '''

        fd, abspath = tempfile.mkstemp(prefix=self._tmpdir, suffix=os.path.splitext(file_)[1], text=True)
        self._tmpfiles.append(abspath)
        os.write(fd, output)
        os.close(fd)

        return abspath

    def _get_filealias(self, file_, version):
        try:
            return self._filealias_cache[file_][version]
        except KeyError:
            self._update_filealias_cache(file_)
            return self._get_filealias(file_, version)

    def _update_filealias_cache(self, file_):
        output = self._git('log --format=hash:%H --follow --name-only -- ' + file_)
        output = iter([line for line in output.splitlines() if len(line) > 0])
        aliases = {}
        for line in output:
            if "hash:" in line:
                hash_ = line.replace("hash:", "")
                alias = output.next()
                aliases[hash_] = alias

        # since filealias_cache *might* be a DictProxy, setdefault does not work
        filecache = self._filealias_cache.get(file_, {})
        filecache.update(aliases)
        self._filealias_cache[file_] = filecache

    def checkout_repo_version(self, version):
        """
        Checkouts the entire repo to a specific version
        The reason for why we would want to do this is due to that some files have strong dependencies between
        themselves that we must take into consideration (for instance dependency between a rhapsody component and its
        scoped models) So by checking out the entire repo we can make sure that the intra-file dependency is consistant.

        To reset repo to whatever branch it was viewing previously you must call uncheckout_repo_version().
        (For extra safety, this is also called as part of the dtor of vcs class)

        Args:
            version(str): The version string (as returned from get_lsv_versions()
        Returns:
            None
        Raises:
            None
        """
        self._git('checkout ' + version)
        self._is_branch_checkedout = True

    def uncheckout_file_version(self, tmp_file=None):
        """
        This cleans out everything that might have been created by checkout_file_version()

        Raises:
            None
        """
        def __remove_files(files):
            for file_ in files:
                self._tmpfiles.remove(file_)
                os.remove(file_)

        if tmp_file is not None:
            __remove_files([tmp_file])
        else:
            __remove_files(self._tmpfiles)

    def uncheckout_repo_version(self):
        """
        This resets the repo version to whatever it was prior to checkoutRepoVerison was called.

        Raises:
            None
        """
        if self._is_branch_checkedout is True:
            self._git('checkout -f ' + self._current_branch)
            self._is_branch_checkedout = False

    def _get_repo_top_dir(self):
        return self._git('rev-parse --show-toplevel')

    def _find_defects_in_commit_history(self, file_, since_date=None):
        defects = {}

        if self._defect_regexp_all is None and \
           self._defect_regexp_subject is None and \
           self._defect_regexp_body is None:
            return defects

        def __match_regex(inputstr, regx, random_defect_id):
            match = regx.search(inputstr)
            if match is not None:
                if regx.groups <= 0:
                    return random_defect_id
                else:
                    defect_ids = [id_.lstrip('0') for id_ in match.groups() if id_ is not None]
                    if len(defect_ids) > 0:
                        # Make sure that all captured groups are identical
                        assert defect_ids.count(defect_ids[0]) == len(defect_ids)
                        return defect_ids[0]

        if self._defect_regexp_all is not None:
            lsv_regexp = self._defect_regexp_all
        else:
            lsv_regexp = '|'.join([rgx for rgx in (self._defect_regexp_subject, self._defect_regexp_body)
                                   if rgx is not None])

        for version in self.get_lsv_versions(file_, since_date, lsv_regexp):
            defect_id = None
            subject = version['subject'].lower()
            body = version['body'].lower()
            versionstr = version['version']

            if self._defect_regexp_all:
                defect_id = __match_regex(subject + body, self._defect_regexp_all_c, versionstr)
            else:
                if self._defect_regexp_subject_c is not None:
                    defect_id = __match_regex(subject, self._defect_regexp_subject_c, versionstr)
                if defect_id is None and self._defect_regexp_body_c is not None:
                    defect_id = __match_regex(body, self._defect_regexp_body_c, versionstr)

            if defect_id is not None:
                defects.setdefault(defect_id, []).append(version)

        return defects

    def _find_root_versions(self, file_):
        # First find root version, this is due to that _git will never even try to do a _git diff on a root version
        output = self._git('rev-list --max-parents=0 HEAD -- ' + file_)
        initial_commits = [line.strip() for line in output.splitlines()]
        return initial_commits
