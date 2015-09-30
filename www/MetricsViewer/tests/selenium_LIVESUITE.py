#!/usr/bin/env python
# pylint: disable=C0111
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
import __init__  # pylint: disable=W0611
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver

class LocalSqliteLiveTest(StaticLiveServerTestCase):
    def test_treemap(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        '''
        Expand to wait for elements to be visible in the treemap.

        ex:
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('myuser')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('secret')
        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()
        '''
    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(LocalSqliteLiveTest, cls).setUpClass()
        cls.selenium.implicitly_wait(20)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LocalSqliteLiveTest, cls).tearDownClass()


if __name__ == "__main__":
    import os
    import sys
    import unittest
    import django

    sys.path.append(os.path.abspath('./../'))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'

    ###############################################################################
    # You could override the live_server_url above by setting the env variable:
    # os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = 'whateverurl:xxx'
    ###############################################################################

    django.setup()
    unittest.main()
