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
  Helper for setting up a mirrored root logger (Meaning, outputs both to file and stdout).
'''
# This * import is used so that any user dont need to import logging as well, they only import logger
# and thus gets all the facilities from logging through logger.
import logging
from logging import *  # pylint: disable=W0401,W0614
import sys


def setup_logger(format_=None, level=None, filename=None):
    '''
    Sets up a new logger
    Args:
        format_(str): a python logging format string
        level(logging.level): The requested loglevel
        filename(str): if supplied, will print to filename AND console
    '''
    if level is None:
        level = INFO
    if format_ is None:
        format_ = "%(levelname)s: %(message)s"

    rootlogger = getLogger()
    rootlogger.setLevel(level)
    log_formatter = Formatter(format_)

    if filename:
        filehandler = FileHandler(filename=filename)
        filehandler.setFormatter(log_formatter)
        rootlogger.addHandler(filehandler)

    consolehandler = StreamHandler(sys.stdout)
    consolehandler.setFormatter(log_formatter)
    rootlogger.addHandler(consolehandler)


def setup_stdout_logger(verbose=False):
    '''
    Sets up a new stdout logger

    Args:
          verbose(Boolean): if True, will set loglevel to DEBUG
    '''
    if verbose:
        level = DEBUG
    else:
        level = None

    setup_logger(level=level)

def disable_logger():
    '''
    Disables logging for ex. during unittests
    '''
    logging.disable(CRITICAL)

def banner(message):
    '''
    Prints a banner with message

    Args:
          message(str): The message to be printed inside the banner
    '''

    banner_frame = "*****************************************************************"
    info(banner_frame)
    info(str('*{:^' + str(len(banner_frame) - 2) + '}*').format(message))
    info(banner_frame)
