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
from LdapWrapperContract import LdapWrapperContract
import subprocess
import os
import getpass
try:
    import pexpect
    pexpect_exists = True
except ImportError:
    pexpect_exists = False


class VasTool(LdapWrapperContract):
    '''
    LDAP realization using calls to vastool
    '''
    def __init__(self, vastool_path="vastool"):
        """
        Args:
            vastool_path(str): path-to-vastool, defaults to "vastool".
        Returns:
            None
        Raises:
            None
        """
        super(VasTool, self).__init__()
        self._vasdb = {}
        self._vastool_path = vastool_path

    def get_email(self, username):
        """
        Tries to find the email for a username, also a powerful tool to check if somebody is in the domain Db at all.

        Args:
            username (str): username to lookup the email on

        Returns:
            email(str): email if found, else "N/A"
        Raises:
            None
        """
        if username not in self._vasdb:
            email = "N/A"
            output = self._exec_vastool("attrs -u " + username + " mail")
            if output is not None and "ERROR:" not in output.split()[0]:
                email = output.split()[1]
            self._vasdb[username] = email
            return email

        else:
            return self._vasdb[username]

    def _exec_vastool(self, command):
        if pexpect_exists:
            child = pexpect.spawn(self._vastool_path + " " + command)
            i = child.expect(['^Password for.*', '.*@.*'])
            if i == 0:
                child.sendline(getpass.getpass())

            return child.after
        else:
            caller = [self._vastool_path]
            caller.extend(command.split(' '))
            try:
                output = subprocess.check_output(caller, stderr=open(os.devnull, 'w'))
            except subprocess.CalledProcessError:
                pass
            else:
                return output
