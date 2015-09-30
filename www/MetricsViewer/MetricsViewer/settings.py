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

  Django settings for MetricsViewer project.

  For more information on this file, see
  https://docs.djangoproject.com/en/1.6/topics/settings/

  For the full list of settings and their values, see
  https://docs.djangoproject.com/en/1.6/ref/settings/

  DO NOT MODIFY THIS FILE DIRECTLY - use local_settings.py instead
  Have a look at local_settings.py.example

  Build paths inside the project like this: os.path.join(BASE_DIR, ...)
'''

import __init__  # pylint: disable=W0611

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = (
    'django.contrib.messages',
    'visualization'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'MetricsViewer.urls'

WSGI_APPLICATION = 'MetricsViewer.wsgi.application'


def _get_db():
    from Utils.ProjectConfig import ProjectConfig
    from DbAPI.MetricsDb import MetricsDb
    return MetricsDb(ProjectConfig().get('MetricsViewer', 'engine_url'))


METRICSDB = _get_db()

REPO_ROOT = __init__.repo_root
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Context processing, used for finding context urls (navbar)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'visualization.context_processors.get_all_urls',
    'visualization.context_processors.last_db_update'
)

# # Load our local_settings
try:
    from local_settings import *  # pylint: disable=W0401,W0614
except ImportError:
    print >> sys.stderr, "Could not import MetricsViewer.local_settings, using defaults!\n" \
                         "To override, you could copy local_settings.py.example -> local_settings.py"
