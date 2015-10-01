#!/usr/bin/env python
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
  This script takes 2 metrics databases and merges them.
'''

import argparse
import os
import shutil
import difflib

import __init__  # pylint: disable=W0611
from Utils import logger
from Utils.sysutils import FancyBar
from DbAPI import MetricsDb
from DbAPI.MetricsDb_ORM import File, ChangeMetric, DefectModification
from sqlalchemy.sql import collate

try:
    from autogenerated_filemapping import queried_filematching
except ImportError:
    queried_filematching = {}


def _parse_args():

    description = """
    Merges old+new db into output_db.
    Takes the old db and tries to find files/functions with closest match in new DB.
    """
    parser = argparse.ArgumentParser(description=description)

    help_str = "Enable verbose mode, mainly for debugging"
    parser.add_argument("-v", action="store_true", dest="verbose", default=False, help=help_str)

    parser.add_argument("--old-db", dest="old_db", required=True, help="oldest input database")
    parser.add_argument("--new-db", dest="new_db", required=True, help="newest input database")
    parser.add_argument("-o|--output", dest="output", required=True, help="output database")

    return parser.parse_args()


def main():  # pylint: disable=C0111
    args = _parse_args()
    logger.setup_stdout_logger(args.verbose)

    args.old_db = os.path.abspath(args.old_db)
    args.new_db = os.path.abspath(args.new_db)
    args.output = os.path.abspath(args.output)

    print "Using old:", args.old_db, "new:", args.new_db, "out:", args.output
    print "Copying", args.new_db, "to", args.output
    shutil.copyfile(args.new_db, args.output)

    db_old = MetricsDb.MetricsDb('sqlite:///' + args.old_db)
    db_out = MetricsDb.MetricsDb('sqlite:///' + args.output)

    with db_old.get_session() as old_session, db_out.get_session() as out_session:
        print "\nTrying to match files between old and new database..."
        # Manual file mapping
        filemap = {}
        failed_mappings = 0

        old_files = {file_: None for file_, in old_session.query(File.file)}
        new_files = {file_: None for file_, in out_session.query(File.file)}

        for oldfile in old_files:
            finalmatch = oldfile

            if oldfile in queried_filematching:
                finalmatch = queried_filematching[oldfile]

            elif oldfile not in new_files:
                searchstring = '%' + os.sep + os.path.basename(oldfile) + '%'
                matches = [match for match, in out_session.query(File.file)\
                                                          .filter(File.file.like(searchstring))\
                                                          .order_by(collate(File.file, 'NOCASE'))]
                # Filter out any files that already have a perfect match between old_files and new_files
                matches = [file_ for file_ in matches if file_ not in old_files]

                if len(matches) > 0:
                    close_matches = difflib.get_close_matches(oldfile, matches)[:10]
                    if len(close_matches) > 0:
                        if len(close_matches) == 1:
                            finalmatch = close_matches[0]
                        else:
                            choice = _query_user_for_filemapping(oldfile, close_matches)

                            if choice == 0:
                                finalmatch = oldfile
                            else:
                                finalmatch = matches[choice - 1]

                            queried_filematching[oldfile] = finalmatch
                else:
                    failed_mappings += 1

            filemap[oldfile] = finalmatch

        _generate_filemapping('autogenerated_filemapping.py', queried_filematching)
        print "Failed to map", failed_mappings, "out of", len(old_files)

        print "Selecting defect modifications from", args.old_db, "and inserting into", args.output

        for defect in FancyBar().iter(old_session.query(DefectModification).all()):
            db_out.insert_defect_modification(out_session,
                                              filemap.get(defect.file.file, defect.file.file),
                                              defect.version.version,
                                              defect.function.function,
                                              defect.defect_id,
                                              defect.user.user,
                                              defect.date)

        out_session.commit()

        print "Selecting change_metrics from", args.old_db, "and inserting into", args.output

        for cm in FancyBar().iter(old_session.query(ChangeMetric).all()):
            db_out.insert_change_metric(out_session,
                                        filemap.get(cm.file.file, cm.file.file),
                                        cm.version.version,
                                        cm.function.function,
                                        date_=cm.date,
                                        user=cm.user.user,
                                        added=cm.added,
                                        changed=cm.changed,
                                        deleted=cm.deleted,
                                        nloc=cm.nloc,
                                        token_count=cm.token_count,
                                        parameter_count=cm.parameter_count,
                                        cyclomatic_complexity=cm.cyclomatic_complexity)
        out_session.commit()
        print "done"


def _query_user_for_filemapping(oldfile, close_matches):
    print "old:", oldfile
    for index, match in enumerate(close_matches):
        print index + 1, " :", match
    print "0  : keep original"
    while True:
        try:
            choice = int(raw_input().lower())
            if choice > len(close_matches):
                choice = None
        except ValueError:
            choice = None

        if choice is not None:
            break
        else:
            print "Incorrect choice, please use integer between 0 and", len(close_matches)
    return choice


def _generate_filemapping(filename, filemapping):
    if len(filemapping) > 0:
        generatedfile = "# pylint: disable-all\n"
        generatedfile = "# This file is automatically generated!\n"
        generatedfile += "# It stores a filemapping between CC and git where it is hard to track renames across VCSs\n"
        generatedfile += "queried_filematching = {\n"

        for file_, newfile in filemapping.iteritems():
            generatedfile += "    '" + file_ + "': '" + newfile + "',\n"

        generatedfile += "}\n"

        with open(filename, "w") as fd:
            fd.write(generatedfile)


if __name__ == "__main__":
    main()