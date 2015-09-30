#!/bin/env python
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
import json
import datetime

def _to_none_if_empty(attribute):
    if attribute == "":
        return None
    else:
        return attribute

def call_custom_bug_tracker(call_str):
    '''
    Calls a custom bug tracker using the supplied string, it then parses and transforms output into python types.
    If any field is empty, i.e "", it will be transformed into None type.

    Assumes that the called BTS parser writes a json array of dictionarys on stdout, with the following format:
    [ {'id': some_int,
       'submitted_on': %Y-%m-%d %H:%M:%S,
       'product': str( len <= 50),
       'severity': str( len <= 50),
       'product': str( len <= 50),
       'answer_code': str( len <= 50),
       'fault_code': str( len <= 50)},
      {'id': some_int,
       'submitted_on': %Y-%m-%d %H:%M:%S,
       'product': str( len <= 50),
       'severity': str( len <= 50),
       'product': str( len <= 50),
       'answer_code': str( len <= 50),
       'fault_code': str( len <= 50)},
       ....]

    Args: call_str (str): path, including arguments to the custom bug tracker parser

    Returns: defects (list):
                            dict('id': some_int, 'submitted_on': datetime, 'product': str, 'severity': str,
                                 'product': str, 'answer_code': str, 'fault_code': str)
    '''
    # attributes in this list will be automatically transformed using the supplied function
    transform_dict = {'id': lambda(x): int(x),  # pylint: disable=W0108
                      'submitted_on': lambda(x): datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")}

    try:
        data = subprocess.check_output(call_str.split())
        json_data = json.loads(data)
    except:
        return ()

    # Loading successfull, now transform & clean data prior to returning it
    for row in json_data:
        for key_ in row.iterkeys():
            try:
                row[key_] = transform_dict[key_](row[key_])
            except KeyError:
                row[key_] = _to_none_if_empty(row[key_])

    return json_data
