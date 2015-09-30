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
import csv
import time
import dateutil.parser

from django.http import HttpResponse
import simplejson as json

from django.conf import settings
from Utils import logger

def session_decorator(fn):
    '''
    Supplies a sqlalchemy session
    '''
    def wrapped(*args, **kwargs):  # pylint: disable=C0111
        with settings.METRICSDB.get_session() as session:
            return fn(session, *args, **kwargs)
    return wrapped

def get_query_columns(query):
    '''
    Gets all the column names for a query
    '''
    return [col["name"] for col in query.column_descriptions]

def str2datetime(datestr):
    '''
    Parses a str containing a IS08601 formatted date and returns a datetime object.

    Args:
        date_str(str)
    Returns:
        datetime.datetime
    '''
    if datestr is None:
        return None

    return dateutil.parser.parse(datestr, fuzzy_with_tokens=False)

def datetime2str(dateobj):
    '''
    takes a datetime object and transform it into iso8601 string format

    Args:
        datetime.datetime
    Returns:
        str
    '''
    return dateobj.isoformat()


def adapt_data(date_dict):
    '''
    Converts a date dict returned by Metricsdb_OrmWrapper.py functions into
    an array of (date, value) and changes the datetime to a timestamp
    '''
    vals = []
    for date_, val in date_dict.iteritems():
        vals.append([time.mktime(date_.timetuple()), val])
    return vals


def dump_data(data, response_type='application/json', filename=None):
    '''
    Function used when dumping raw data to the clients. It can handle both csv and json data and dumps the correct
    format according to the response_type parameter passed by the client. The HttpResponse is flagged with the content
    type and can usually be parsed automatically on the frontend using jquery.ajax() which guesses the correct response
    type based on the `content_type` in the `HttpResponse`.
    '''
    if response_type in ('csv', 'text/csv'):
        response = HttpResponse(content_type=response_type)
        filename = filename or "file"
        response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(filename)
        response = _toCSV(data, response)

    elif response_type in ('json', 'application/json'):
        response = HttpResponse(_toJSON(data), content_type=response_type)
    else:
        logger.warn('Unknown response_type %s', response_type)

    return response


class _SqlAlchemyJSONEncoder(json.JSONEncoder):
    '''
    Custom JSONEncoder subclass which can handle formats provided by SQLAlchemy.
    '''
    def default(self, obj):  # pylint: disable=E0202
        if hasattr(obj, 'isoformat') and callable(obj.isoformat):
            return obj.isoformat()
        elif hasattr(obj, 'tojson') and callable(obj.tojson):
            return obj.tojson()
        else:
            return json.JSONEncoder.default(self, obj)


def _toJSON(data):
    return json.dumps(data, namedtuple_as_object=False, use_decimal=True, cls=_SqlAlchemyJSONEncoder)


def _toCSV(data, response):
    '''
    Since the csv writer needs a buffer like object it can't be dropped inline like the json.
    '''
    writer = csv.writer(response)
    for row in data:
        writer.writerow(row)
    return response
