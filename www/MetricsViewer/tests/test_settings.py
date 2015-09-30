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
  This is the settings file used for unittests
'''

import __init__  # pylint: disable=W0611

DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = ['*']

SECRET_KEY = 'test_test'

ROOT_URLCONF = 'MetricsViewer.urls'
STATIC_URL = '/static/'

# Application definition
INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'visualization',
    'tests'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
)

# This is actually not used, but put here since the LiveServerTestCase class assumes a django ORM backend.
# But since we actually dont have a ORM defined, this is essentially a no-op.
SOUTH_TESTS_MIGRATE = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

# Context processing, used for finding context urls (navbar)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'visualization.context_processors.get_all_urls',
)

REPO_ROOT = __init__.repo_root
