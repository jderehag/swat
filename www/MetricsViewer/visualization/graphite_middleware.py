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
import uuid
from django.http import Http404
from django_statsd.clients import statsd
from user_agents import parse

COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # 1 year
COOKIE_KEY = 'uuid'


def _ip_address_from_request(request):
    meta = request.META

    # figure out the IP
    if 'HTTP_TRUE_CLIENT_IP' in meta:
        # Akamai's Site accelorator's proxy header for real IP
        ip_address = meta.get('HTTP_TRUE_CLIENT_IP', '')
    elif 'REMOTE_ADDR' in meta and meta.get('REMOTE_ADDR', '') != '127.0.0.1':
        ip_address = meta.get('REMOTE_ADDR', '')
    elif 'HTTP_X_REAL_IP' in meta:
        ip_address = meta.get('HTTP_X_REAL_IP', '')
    elif 'HTTP_X_FORWARDED_FOR' in meta:
        ip_address = meta.get('HTTP_X_FORWARDED_FOR', '')
    else:
        ip_address = meta.get('REMOTE_ADDR', None)

    return ip_address


class GraphiteMiddleware(object):
    '''
    Handles all requests as middleware and manages statsd counters
    '''
    def process_response(self, request, response):  # pylint: disable=C0111
        statsd.incr('response.%s' % response.status_code)
        self._count_user_agent(request)
        self._count_visitor(request, response)
        return response

    def process_exception(self, _, exception):  # pylint: disable=C0111
        if not isinstance(exception, Http404):
            statsd.incr('response.500')

    def _count_user_agent(self, request):
        # Do some UA parsing to find explicit browser version?
        # Is fairly complicated due to that token ordering is not standardized
        # and even differs across versions within the same browser
        # Mozilla/[version] ([system and browser information]) [platform] ([platform details]) [extensions]
        # RFC 7231: User-Agent = product *( RWS ( product / comment ) )
        try:
            ua = parse(request.META['HTTP_USER_AGENT'])

            ua_str = str(ua.browser.family + "_" + ua.browser.version_string).replace(' ', '_').partition('.')[0]
            statsd.incr('user_agent.browser.%s' % ua_str)

            os_str = str(ua.os.family + "_" + ua.os.version_string).replace(' ', '_').partition('.')[0]
            statsd.incr('user_agent.OS.%s' % os_str)
        except:
            pass

    def _count_visitor(self, request, response):
        uuid_cookie = request.COOKIES.get(COOKIE_KEY, None)
        if uuid_cookie:
            statsd.set('visitors', uuid_cookie)
        else:
            '''
            This is a bit dangerous, since this might mean that a visitor will be counted twice.
            First request->no-cookie [count for ip-addr], second request ->cookie there [count for uuid].
            So the same visitor will always be counted twice.
            To fix that, it would require us to keep stateful information on serverside for the duration
            during first and second request.
            But atleast we will count a visitor based on ip in those cases cookies are disabled.
            '''
            addr = _ip_address_from_request(request) or "N/A"
            statsd.set('visitors', addr)
            response.set_cookie(COOKIE_KEY, str(uuid.uuid4()), max_age=COOKIE_MAX_AGE, httponly=True)
