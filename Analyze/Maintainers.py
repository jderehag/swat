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
import glob
import re
import os
from Utils import logger
from Analyze import EnvParser
import codecs


class _Rule(object):
    """
    A rule consists of a path and a rule type (include/exclude),
    and a reference to the maintainer_entry that the rule belongs to
    """
    def __init__(self, path, maintainer_entry, rule_type):
        if path.startswith('/'):
            path = path[1:]
        if path.endswith('/'):
            path = path[:-1]

        # This variable is only used during initialization, to put the rule in the right _RuleTreeNode
        self.path_components = path.split('/')

        self.maintainer_entry = maintainer_entry
        self.include = rule_type == 'include'
        self.exclude = rule_type == 'exclude'
        assert self.include or self.exclude


class _RuleTreeNode(object):
    """
    A node in a tree that represents the set of rules in a maintainer file.
    Each node corresponds to a file or a directory in the file system,
    and contains a list of the Rule objects that explicitly refers to this path
    """

    def __init__(self, name, parent, children):
        self.name = name
        self.parent = parent
        self.children = children

        # The rules that explicitly refers to this node.
        self.rules = []

    def insert(self, rule, path_components=None):
        """
        Inserts a rule in the right place in the tree, creating new nodes as necessary.
        """

        if path_components is None:
            path_components = rule.path_components

        if len(path_components) == 0:
            self.rules.append(rule)
            return
        first = path_components[0]
        for child in self.children:
            if child.name == first:
                child.insert(rule, path_components[1:])
                return
        new_child = _RuleTreeNode(first, self, [])
        new_child.insert(rule, path_components[1:])
        self.children.append(new_child)

    def find_best_match(self, path_components):
        """
        Takes a list of path components (e.g. ['usr', 'bin', 'env']), and returns the best matching node
        (i.e. the one that matches the longest part of the path).
        """
        if not path_components:
            return self
        first = path_components[0]
        for child in self.children:
            if child.name == first:
                return child.find_best_match(path_components[1:])
        return self


class _RuleEvaluator(object):
    """
    Evaluates which maintainer entry(ies) is active for a set of rules.
    This is used by going step by step from the root directory to the
    most specific directory/file, calling add_rules() for each step
    on the way.
    """

    def __init__(self, other=None):
        self._maint_entries_list = []
        if other: # deep copy
            for me in other.get_maintainer_entries_list():
                self._maint_entries_list.append(list(me))

    def get_maintainer_entries_list(self):
        "Returns the list of maintainer entries"
        return self._maint_entries_list

    def add_rules(self, rules):
        "Adds a set of rules, which will have higher precedence than previous ones"
        new_maint_entries = []
        for rule in rules:
            if rule.include:
                new_maint_entries.append(rule.maintainer_entry)
            else:
                for maint_entries in self._maint_entries_list:
                    maint_entries[:] = [me for me in maint_entries if not me is rule.maintainer_entry]
        self._maint_entries_list.append(new_maint_entries)

    def get_active_maintainer_entries(self):
        "Returns list of currently active maintainer entries"
        for maint_entries in reversed(self._maint_entries_list):
            if maint_entries:
                return maint_entries
        return []


class _VerifyResult(object):
    "Stores the paths that failed verification"
    def __init__(self):
        self.no_maintainer = []
        self.multiple_maintainers = []


def _find_matching_maintainer(node):
    """
    Finds the maintainer entry(ies) for a specific node.
    """
    nodes = []
    while node:
        nodes.insert(0, node)
        node = node.parent

    evaluator = _RuleEvaluator()
    for n in nodes:
        evaluator.add_rules(n.rules)
    return evaluator.get_active_maintainer_entries()


def _verify(node, path, files, evaluator, result):
    """
    Finds all files/directories that have either zero or several equally matching maintainer_entry's.

    Searches recursively starting from the 'node' parameter, ignoring any files in the file system that
    are not in the 'files' list.

    Args:
        node:      The _RuleTreeNode where the search starts
        path:      The file system path of 'node'
        files:     A list of all applicable file paths, any files founds not in this list are ignored
        evaluator: _RuleEvaluator (already initialized with the rules of any parent nodes)
        result:    _VerifyResult output parameter
    """

    def join(path, filename):
        "Like os.path.join(), but faster for some reason"
        if path == os.path.sep:
            return path + filename
        else:
            return path + os.path.sep + filename

    # Update the evaluator with current node, and get the number of active maintainer entries
    evaluator.add_rules(node.rules)
    num_active_maintainer_entries = len(evaluator.get_active_maintainer_entries())

    def check_add_path(path):
        "Adds a path to a output list if necessary"
        if num_active_maintainer_entries != 1:
            if path in files:
                error_list = result.no_maintainer if num_active_maintainer_entries == 0 else result.multiple_maintainers
                error_list.append(path)

    if os.path.isdir(path):
        children = os.listdir(path)
        if children:
            if node.children:
                # Check all child rules that refers to existing files
                for node_child in node.children:
                    if node_child.name in children:
                        _verify(node_child, join(path, node_child.name), files, _RuleEvaluator(evaluator), result)
            # Check all existing files that does not have explicit rules
            for child in children:
                if not child in [c.name for c in node.children]:
                    check_add_path(join(path, child))
    else:
        check_add_path(path)


class Maintainers(object):
    """
    Takes a maintainerfile and parses it.
    Exits application if maintainerfile could not be opened.
    """

    def __init__(self, maintainerfile):
        self._maintainerfile = os.path.expandvars(maintainerfile)
        self._maintainer_entrys = []
        self._env_parser = EnvParser.EnvPathParser()

        try:
            file_ = codecs.open(self._maintainerfile, encoding='utf-8', mode='r')
        except IOError:
            logger.critical("Could not open %s this should be impossible at this stage!", self._maintainerfile)
            exit(-1)

        maintainerfile = []

        # Filter out empty lines and comments
        while 1:
            lines = file_.readlines()
            if not lines:
                break
            for line in lines:
                if len(line.lstrip()) != 0:
                    if line.lstrip()[0] != '#':
                        maintainerfile.append(line.strip().encode('utf-8'))
        self._read_maintainer_scopes(maintainerfile)
        self._verify_paths()
        self._tree = self._make_rule_tree()

    def get_maintainer_list(self):
        """
        Returns the parsed maintainerlist.

        Args:
            None
        Returns:
            maintainerentrys(list(entry)): entry(dict) =
                                            entry['subsystem'](str)
                                            entry['maintainer'](list(str))
                                            entry['maillist'](str)
                                            entry['status'](str)
                                            entry['file-include-pattern'](list(str))
                                            entry['file-exclude-pattern'](list(str))

        Raises:
            None

        """
        return self._maintainer_entrys

    def get_maintainer_entry(self, subsystem_name):
        """
        Searches for a maintainer entry matching subsystem.

        Args:
            subsystem_name(str): name of the subsystem to try to find the entry for
        Returns:
            subsystem entry(dict):
                                entry['subsystem'](str)
                                entry['maintainer'](list(str))
                                entry['maillist'](str)
                                entry['status'](str)
                                entry['file-include-pattern'](list(str))
                                entry['file-exclude-pattern'](list(str))

        Raises:
            None
        """
        for entry in self.get_maintainer_list():
            if entry['subsystem'] == subsystem_name:
                return entry
        return None

    def verify_maintainers(self, files):
        """
        Verifies that each file is covered by exactly one subsystem
        """
        result = _VerifyResult()
        _verify(self._tree, '/', files, _RuleEvaluator(), result)
        return result.no_maintainer, result.multiple_maintainers

    def find_matching_maintainers(self, filename):
        """
        Searches for any maintainer responsible for filename

        Really not happy with this implementation, basically does a linear search finding matches.
        Should instead be implemented using radix tree..

        Args:
            filename(str): name of the file to check responsibility for
        Returns:
            matching_maintainer(list): entry(dict):
                                            entry['subsystem'](str)
                                            entry['maintainer'](list(str))
                                            entry['maillist'](str)
                                            entry['status'](str)
                                            entry['file-include-pattern'](list(str))
                                            entry['file-exclude-pattern'](list(str))
        Raises:
            None
        """

        if filename.startswith('/'):
            filename = filename[1:]
        path_components = filename.split('/')
        node = self._tree.find_best_match(path_components)
        mes = _find_matching_maintainer(node)
        return mes

    def _read_maintainer_scopes(self, text):
        # Really not happy with this parsing,
        # should be much easier doing it properly using recursion
        # Actually, investigate if this entire class can be changed so that it used ConfigParser instead, but *must*
        # keep original linux kernel MAINTAINERS file structure!
        line_index = 0
        while line_index in range(0, len(text)):
            if text[line_index][0] == '[':  # scope begin!
                maintainer_scope = []
                maintainer_scope.append(text[line_index])
                line_index = line_index + 1
                # Get all lines below "scope begin" until we reach next scope
                while line_index in range(0, len(text)):
                    if text[line_index][0] != '[':
                        maintainer_scope.append(text[line_index])
                        line_index = line_index + 1
                    else:

                        break
                self._maintainer_entrys.append(self._parse_maintainer_scope(maintainer_scope))
            else:
                line_index = line_index + 1

    def _parse_maintainer_scope(self, text):
        maintainer = {}
        maintainer['subsystem'] = ""
        maintainer['maintainer'] = []
        maintainer['maillist'] = ""
        maintainer['status'] = ""
        maintainer['file-include-pattern'] = []
        maintainer['file-exclude-pattern'] = []

        for lnumber, line in enumerate(text):
            if line[0] == '[':  # subsystem name
                maintainer['subsystem'] = line[1:line.rfind(']')].strip()
            elif line[0:2] == 'M:':  # Maintainer
                maintainer['maintainer'].append((line[2:line.find('<')].strip(),
                                                 line[line.find('<') + 1:line.find('>')].strip()))
            elif line[0:2] == 'L:':  # mailinglist
                maintainer['maillist'] = line[2:].strip()
            elif line[0:2] == 'S:':  # Status
                maintainer['status'] = line[2:].strip()
            elif line[0:2] == 'F:':  # File pattern
                maintainer['file-include-pattern'].append(self._env_parser.parse(line[2:].strip()))
            elif line[0:2] == 'X:':  # Exclude pattern
                maintainer['file-exclude-pattern'].append(self._env_parser.parse(line[2:].strip()))
            else:
                logger.warn("Unable to intrpret line %s [must start with one of [MLSFX :[%s]", lnumber, line)
        return maintainer

    def _verify_paths(self):
        is_ok = True

        filepaths = []
        for maint in self.get_maintainer_list():
            filepaths.extend(maint['file-include-pattern'])
            filepaths.extend(maint['file-exclude-pattern'])

        all_envs = {}
        for path in filepaths:
            match = re.match(r'.*\$(\w+).*', path)
            if match is not None and match.group(1) is not None:
                all_envs[match.group(1)] = None

        for env in all_envs.iterkeys():
            if env not in os.environ:
                logger.critical("Could not find $%s envrionment variable! Perhaps you need to run setup_workspace?",
                                env)
                is_ok = False

        assert is_ok

    def _make_rule_tree(self):
        tree = _RuleTreeNode('', None, [])
        for maint in self.get_maintainer_list():
            for pattern in maint['file-include-pattern']:
                for path in glob.glob(pattern):
                    tree.insert(_Rule(path, maint, 'include'))
            for pattern in maint['file-exclude-pattern']:
                for path in glob.glob(pattern):
                    tree.insert(_Rule(path, maint, 'exclude'))
        return tree
