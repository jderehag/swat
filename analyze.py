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
  analyze.py forms the analytics pipeline. It will update repo, parse repo history, analyze each file version
  and then push any new info into a database.
  It will also scrape any BTS, and optionally mirror DB:s..
'''
import argparse
import os
import traceback

from datetime import timedelta, datetime
from multiprocessing import Manager, Pool

from Utils.ProjectConfig import ProjectConfig, default_config
from Utils import logger, sysutils
from Utils.sysutils import FancyBar

from Analyze import Maintainers, SrcRootWalker
from Analyze.Backends.VCS import VcsWrapper
from Analyze.Backends.BTS import CustomBugTracker
from Analyze.Backends.LdapWrapper import LdapWrapper
from Analyze.Metrics import ChangeRate, LizardWrapper

from DbAPI import MetricsDb
from DbAPI.MetricsDb_ORM import Subsystem, File, DefectMeta, User

def _main():
    args, config = _parse_args()

    """
    #####################################################
    Config
    #####################################################
    """
    config_engine_url = config.get('Analyze', 'engine_url', '')
    config_mirror_engine_url = config.get('Analyze', 'mirror_engine_url', None)
    config_custom_bts_scraper = config.get('Analyze', 'custom_bts_scraper', None)
    config_threads = config.getint('Analyze', 'threads')
    config_lookup_email = config.getboolean('Analyze', 'lookup_email')
    config_loglevel = config.getloglevel('Analyze', 'log_level')
    config_logpath = config.get('Analyze', 'log_path')
    config_logformat = config.get('Analyze', 'log_format')
    config_transformerdict = config.getdict('Analyze', 'code_transformer', ())
    config_mirror = args.mirror
    config_update_repo = args.update_repo
    config_scrape_bts = args.scrape_bts

    if args.files:
        config_debugging_single_file = True
    else:
        config_debugging_single_file = False

    logger.setup_logger(format_=config_logformat, level=config_loglevel, filename=config_logpath)

    logger.banner("Running " + os.path.basename(__file__))
    logger.info("Options:")
    logger.info("  Database: %s", config_engine_url[:config_engine_url.find(':')])
    logger.info("  threads: %s", config_threads)
    logger.info("  lookup_email: %s", config_lookup_email)
    if config_mirror and config_mirror_engine_url is not None:
        # Do not print the engine_url since it may contain user/pass
        logger.info("  DB mirroring: Yes")
    logger.info("  scrape bug tracking system: %s", config_scrape_bts)
    logger.info("  Update repo prior to analysis: %s", config_update_repo)

    os.nice(10)

    """
    #####################################################
    Setup instances
    #####################################################
    """
    vcs = VcsWrapper.VcsFactory(config=config, shared_dict_ctor=Manager().dict)
    maintainerobj = Maintainers.Maintainers(config.get('General', 'maintainers'))
    walker = SrcRootWalker.SrcRootWalker(config.getlist('Analyze', 'include_patterns'),
                                         config.getlist('Analyze', 'exclude_patterns', ()))

    db = MetricsDb.MetricsDb(config_engine_url)
    pool = Pool(processes=config_threads)

    last_metric_update = None

    """
    #####################################################
    Update repo
    #####################################################
    """
    if config_update_repo:
        logger.info('Updating repo prior to analysis...')
        vcs.update_repo(repo_root=config.get('Git', 'repo_root'))
        logger.info('Updating repo done')

    start = datetime.now()

    """
    #####################################################
    Scrape Bug Tracking System for defects and add to metrics.db
    #####################################################
    """
    if config_scrape_bts and config_custom_bts_scraper is not None:
        _scrape_meta_defects(db, config_custom_bts_scraper)

    """
    #####################################################
    Start analysis
    #####################################################
    """

    if config_lookup_email:
        _lookup_emails(db)
    else:
        logger.info("Looking up files to analyze...")
        if config_debugging_single_file:
            all_files = args.files
        else:
            last_metric_update = db.get_eav_value('last_metric_update')
            if last_metric_update is not None:
                # subtract an extra day to make sure that we dont miss anything during the overlap of the analysis
                last_metric_update = last_metric_update - timedelta(days=1)

            all_files = walker.find_all_files_in_srcroots()
        logger.info("Found %s files!", len(all_files))

        if len(all_files) != 0:
            _lookup_defect_modifications(pool, walker, vcs, db, all_files, last_metric_update)
            _lookup_metrics(pool, walker, vcs, db, all_files, last_metric_update, config_transformerdict)

        if not config_debugging_single_file:
            logger.info("Doing db cleanup...")
            _remove_unwanted_files(db, {walker.translate_env(file_): None for file_ in all_files})
            _lookup_maintainers(pool, db, maintainerobj)

        logger.info("Finished analysis phase in %s" % (datetime.now() - start))

        if not config_debugging_single_file:
            db.set_eav_value('last_metric_update', start)

    """
    #####################################################
    Mirroring
    #####################################################
    """
    if config_mirror and config_mirror_engine_url is not None:
        logger.info("Mirroring %s -> %s", config_engine_url[:config_engine_url.find(':')],
                    config_mirror_engine_url[:config_mirror_engine_url.find(':')])
        start = datetime.now()
        MetricsDb.MetricsDb(config_mirror_engine_url).copy_from_db(db)
        logger.info("Finished mirroring phase in %s" % (datetime.now() - start))


def _scrape_meta_defects(db, custom_bts_scraper):
    start = datetime.now()
    logger.info("Scraping Bug tracker...")
    defects = CustomBugTracker.call_custom_bug_tracker(custom_bts_scraper)

    with db.get_session() as session:
        DefectMeta.__table__.drop(db.engine, checkfirst=True)
        DefectMeta.__table__.create(db.engine, checkfirst=False)
        session.commit()

        for defect in FancyBar('Inserting:').iter(defects):
            if defect['product'] is not None:
                defect_meta = db.get_or_create(session, DefectMeta, id=defect['id'])
                defect_meta.submitted_on = defect['submitted_on']
                defect_meta.severity = defect['severity']
                defect_meta.product = defect['product']
                defect_meta.answer_code = defect['answer_code']
                defect_meta.fault_code = defect['fault_code']
        session.commit()

    logger.info("Finished scraping BTS in %s" % (datetime.now() - start))


def _lookup_defect_modifications(pool, walker, vcs, db, files, last_update):
    logger.info("Looking up defect modifications...")
    filemap = zip([vcs] * len(files), [last_update] * len(files), files)
    with db.get_session() as session:
        iter_ = FancyBar(max=len(filemap)).iter(pool.imap_unordered(worker(_get_defects), filemap))
        for file_, defects in iter_:
            for defect, entries in defects.iteritems():
                for entry in entries:
                    for function in entry['functions']:
                        db.insert_defect_modification(session,
                                                      file_=walker.translate_env(file_),
                                                      version=entry['version'],
                                                      function=function,
                                                      defect_id=defect,
                                                      user=_translate_username(entry),
                                                      date_=entry['datetime'])
        session.commit()


def _lookup_metrics(pool, walker, vcs, db, files, last_update, config_transformerdict):
    logger.info("Looking up metrics...")
    file_map = zip([vcs] * len(files), [last_update] * len(files), files)

    version_map = []
    logger.info("   Looking up all VCS versions...")

    iter_ = FancyBar(max=len(file_map)).iter(pool.imap_unordered(worker(_get_lsv), file_map))
    for file_, contributions in iter_:
        for contrib_index, contrib in enumerate(contributions):
            prev_version = contributions[contrib_index - 1]['version'] if contrib_index > 0 else None
            filext = os.path.splitext(file_)[1]
            version_map.append((file_, contrib, prev_version, vcs, config_transformerdict.get(filext, None)))

    logger.info("   Looking up all metrics...")
    with db.get_session() as session:
        iter_ = FancyBar(max=len(version_map)).iter(pool.imap_unordered(worker(_get_metrics), version_map))
        for file_, contrib in iter_:
            '''
            Results are coming in, insert results into database
            We avoid doing this inside the process pool due to that sqlite is not threadsafe
            '''
            version = contrib['version']
            date_ = contrib['datetime']
            user = _translate_username(contrib)
            translated_file = walker.translate_env(file_)

            complexity = contrib['complexity']
            changerates = contrib['changerates']

            for function, (added, changed, deleted, nloc) in changerates.iteritems():
                if function not in complexity:
                    if file_.endswith((".c", ".cc", ".cpp", ".h", ".hpp")):
                        logger.debug("%s Could not find complexity function \"%s\"", file_, function)
                        logger.debug("%s Available functions:", os.path.basename(file_))
                        for func in complexity.iterkeys():
                            logger.debug("%s", func)

                    cyclomatic_complexity = None
                    tokens = None
                    parameter_count = None
                    max_nd = None
                    fin = None
                    fout = None
                else:
                    cyclomatic_complexity, tokens, parameter_count, max_nd, fin, fout = complexity[function]

                db.insert_change_metric(session,
                                        file_=translated_file,
                                        version=version,
                                        function=function,
                                        date_=date_,
                                        user=user,
                                        added=added,
                                        changed=changed,
                                        deleted=deleted,
                                        nloc=nloc,
                                        cyclomatic_complexity=cyclomatic_complexity,
                                        token_count=tokens,
                                        parameter_count=parameter_count,
                                        max_nesting_depth=max_nd,
                                        fan_in=fin,
                                        fan_out=fout)
        session.commit()


def _get_defects((vcs, last_update, file_)):
    return (file_, vcs.find_all_defects(file_, since_date=last_update, changeinfo=True))


def _get_lsv((vcs, last_update, file_)):
    return (file_, vcs.get_lsv_versions(file_, since_date=last_update))


def _get_metrics((file_, contrib, prev_version, vcs, transformer)):
    curr_version_file = vcs.checkout_file_version(file_, contrib['version'])

    contrib['changerates'] = _get_changerate(vcs, file_, curr_version_file, prev_version)
    contrib['complexity'] = _get_complexity(curr_version_file, transformer)

    if curr_version_file is not None:
        vcs.uncheckout_file_version(curr_version_file)

    return (file_, contrib)


def _get_changerate(vcs, file_, curr_version_file, prev_version):
    prev_version_file = None
    if os.path.isfile(curr_version_file):
        prev_version_file = None if prev_version is None else vcs.checkout_file_version(file_, prev_version)
        changerate = ChangeRate.ChangeRate(vcs).count_change_rate(prev_version_file, curr_version_file)

        if prev_version_file is not None:
            vcs.uncheckout_file_version(prev_version_file)

        return changerate


def _get_complexity(curr_version_file, transformer):
    return_complexity = {}
    lizard_data = None
    if transformer is not None:
        mockfile = sysutils.call_subprocess(transformer.split() + [curr_version_file])
        lizard_data = LizardWrapper.run_lizard("mock.cpp", mockfile)
    else:
        lizard_data = LizardWrapper.run_lizard(curr_version_file)

    if lizard_data is not None:
        return_complexity = {func['name']: (func['cyclomatic_complexity'],
                                            func['token_count'],
                                            len(func['parameters']),
                                            func.get('max_nesting_depth', None),
                                            func.get('fan_in', None),
                                            func.get('fan_out', None)) for func in lizard_data}
    return return_complexity


def _remove_unwanted_files(db, files):
    logger.info("Cleaning out unwanted files...")
    removed_files = 0

    with db.get_session() as session:
        for file_ in FancyBar().iter(session.query(File)):
            if file_.file not in files:
                removed_files += 1
                session.delete(file_)
        session.commit()
    logger.info("Removed %d files out of %d from db", removed_files, session.query(File).count())


def _lookup_maintainers(pool, db, maintainerobj):
    logger.info("Updating maintainers...")
    with db.get_session() as session:
        file_tuples = db.get_file_ids_and_abspaths(session)

        logger.debug("Remove subsystem mappings..")
        for file_ in session.query(File):
            file_.subsystem = None
        session.commit()

        Subsystem.__table__.drop(db.engine, checkfirst=True)
        Subsystem.__table__.create(db.engine, checkfirst=False)

        logger.debug("Populating maintainers table...")
        for maintainer_info in maintainerobj.get_maintainer_list():
            db.insert_subsystem_entry(session,
                                      subsystem=maintainer_info["subsystem"],
                                      status=maintainer_info["status"],
                                      maintainers=[maint for maint, _ in maintainer_info["maintainer"]])
        session.commit()

        logger.debug("Looking up maintainer for all files")
        filemap = zip([maintainerobj] * len(file_tuples), file_tuples)

        count_some_maintainer = 0
        iter_ = FancyBar(max=len(filemap)).iter(pool.imap_unordered(worker(_get_maintainers), filemap))
        for file_tuple, maintainer_dicts in iter_:
            if maintainer_dicts is not None:
                count_some_maintainer += 1
                file_id = file_tuple[0]
                for maintainer_dict in maintainer_dicts:
                    db.update_file_entry(session, file_id=file_id, subsystem_name=maintainer_dict["subsystem"])
        session.commit()

        logger.info("Amount of files with a maintainer: %d", count_some_maintainer)
        logger.info("Amount of files without a maintainer: %d", len(file_tuples) - count_some_maintainer)


def _get_maintainers((maintainer_obj, file_tuple)):
    return (file_tuple, maintainer_obj.find_matching_maintainers(file_tuple[1]))


def _lookup_emails(db):
    logger.info("Transform usernames to email addresses...")
    non_email_users = 0
    transformed_users = 0
    removed_users = []
    ldap = LdapWrapper.LdapWrapper()
    with db.get_session() as session:
        for user in session.query(User).filter(User.user.notlike('%@%')):
            non_email_users += 1
            email = ldap.get_email(user.user)
            if email != "N/A":
                email = email.decode('unicode-escape').lower()
                existing_user = session.query(User).filter(User.user == email).first()
                if existing_user:
                    # If the user already exist, we need to move all entries to this user instead.
                    for defect in user.defect_mods:
                        defect.user = existing_user
                    for cm in user.change_metrics:
                        cm.user = existing_user
                    removed_users.append(user.id)
                else:
                    transformed_users += 1
                    user.user = email
        session.commit()
        session.expire_all()
        for id_ in removed_users:
            session.delete(session.query(User).filter(User.id == id_).one())
    logger.info("Found %d non email-users, transformed %d, removed %d", non_email_users,
                transformed_users, len(removed_users))


def _translate_username(entry):
    # Try to use email instead of username due to that emails are consistent between CC & git
    user = entry['user']
    if 'email' in entry:
        user = entry['email']
    return user


class worker(object):
    '''
    Unfortunatly, multiprocess pool works poorly with decorated functions due to that it pickles the information
    between processes. So when decorating a function, that actually makes that function unpickable, so we avoid that
    by creating a worker class instead, which is more akin to "decorator pattern" rather than a python decorator
    (designated with @). Unfortunatly it forces us to explicitly call any decorated function as worker(func) and
    decoration is not done automatically.
    '''
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        try:
            return self.func(*args, **kwargs)
        except Exception as e:  # pylint: disable=W0703
            logger.critical(traceback.format_exc())
            logger.critical("Cought exception in worker %s", e)
            logger.critical("Args: %s", args)
            exit(-1)

class _PathAction(argparse.Action):
    def __call__(self, _, namespace, values, option_string=None):
        setattr(namespace, self.dest, [os.path.abspath(val) for val in values])

def _parse_args():
    parser = argparse.ArgumentParser(add_help=True)

    help_str = "Enable verbose mode, (forces logger to use DEBUG level)"
    parser.add_argument('-v', action="store_true", dest='verbose', default=False, help=help_str)

    help_str = "config file"
    parser.add_argument('--config', dest='config', default=default_config, help=help_str)

    help_str = "Force use of sqlite (overrides value in config file)"
    parser.add_argument('--sqlite', dest='sqlite', default=None, help=help_str)

    help_str = "Execute with number-of-threads (overrides value in config file), (default=ncpu)"
    parser.add_argument('--threads', dest='threads', type=int, default=None, help=help_str)

    help_str = "Resolve usernames into emails to have consistant values over VCSs." \
               "This is explicit here due to that email lookups are buggy, so its usually " \
               "better to do that in a seperate step"
    parser.add_argument('--email', dest='email', action="store_true", default=False, help=help_str)

    help_str = "Mirror sqlite db to mysql, drops all tables in and rebuilds (default=False)"
    parser.add_argument('--mirror', action="store_true", dest='mirror', default=False, help=help_str)

    help_str = "Update repo prior to updating db"
    parser.add_argument('--update-repo', action="store_true", dest='update_repo', default=False,
                        help=help_str)

    help_str = "Scrape BTS for defects (default=False)"
    parser.add_argument('--scrape-bts', action="store_true", dest='scrape_bts', default=False, help=help_str)

    parser.add_argument('files', nargs='*', help="Files to update", action=_PathAction)

    args = parser.parse_args()

    config = ProjectConfig(config=args.config)

    if args.threads:
        config.set('Analyze', 'threads', str(args.threads))
    if args.sqlite:
        config.set('Analyze', 'dbtype', 'sqlite')
        config.set('Metrics sqlite', 'path', args.sqlite)
    if args.email:
        config.set('Analyze', 'lookup_email', str(args.email))
    if args.verbose:
        config.set('Analyze', 'log_level', 'DEBUG')

    return args, config

if __name__ == '__main__':
    _main()
