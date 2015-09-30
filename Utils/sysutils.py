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
import sys
import logger
from progress.bar import Bar


def call_subprocess(args, with_errno=False, **kwargs):
    '''
    Spawn args, this function basically adds printing and exception handling around subprocess.
    '''
    logger.debug("Calling: %s", args)
    try:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, close_fds=True, **kwargs)
    except Exception, e:
        logger.warn("call_subprocess failed, args: %s, exception:%s", args, e)
        raise
    else:
        try:
            output, _ = process.communicate()
        except Exception, e:
            logger.warn("call_subprocess->communicate failed args: %s, exception: %s", args, e)
            raise

    logger.debug("Finished calling: %s rc=%s", args, process.returncode)
    if with_errno:
        return process.returncode, output
    else:
        return output

def _get_term_width():
    try:
        from struct import unpack
        from fcntl import ioctl
        from termios import TIOCGWINSZ
        return unpack("hh", ioctl(sys.stdout.fileno(), TIOCGWINSZ, "    "))[1]
    except:
        return None

class FancyBar(Bar):
    '''
    A console progressbar subclassed from progress 1.2
    Basically added partial support for getting terminal width, only supported on some *nix systems.
    and a different default suffix .
    '''
    fill = '#'
    suffix = '%(index)d/%(max)d - %(percent).1f%% - %(eta_td)s'
    width = _get_term_width() or 120
    width -= len(suffix)
