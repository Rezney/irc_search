from django.core.management import BaseCommand
from core.models import IRCMessage
from django.db import IntegrityError
from datetime import datetime
from core.constants import MESSAGES

import re
import os
import shutil
import logging
import tarfile

logger = logging.getLogger('django')


def format_time(date, time):
    datetime_object = datetime.strptime('{} {}'.format(date, time),
                                        '%Y-%m-%d %H:%M:%S')
    return datetime_object


def archive_log_file(log_fpath, channel_dir):
    consumed_dir = os.path.join(channel_dir, 'consumed')
    try:
        os.makedirs(consumed_dir)
    except OSError:
        pass
    tarball_fpath = os.path.join(log_fpath + '.tar.gz')
    log_fname = log_fpath.split(os.sep)[-1]
    with tarfile.open(tarball_fpath, 'w:gz') as tar_file:
        tar_file.add(log_fpath, arcname=log_fname)
    shutil.copy(tarball_fpath, consumed_dir)
    os.unlink(log_fpath)
    os.unlink(tarball_fpath)


def save_multiple_msgs(lst):
    try:
        IRCMessage.objects.bulk_create(lst)
    except IntegrityError:
        for m in lst:
            try:
                m.save()
            except IntegrityError:
                pass


def into_db(log_path, channel):
    # get date from filename
    date = log_path.split('/')[-1].split('.')[0]
    logger.info('Consuming: {}'.format(log_path))
    message_list = []
    with open(log_path, encoding='utf-8', errors='ignore') as fd:
        valid = False
        for line in fd.readlines():
            # split lines on first 2 whitespaces to get date, nick and message
            line_lst = line.rstrip().split(' ', 2)
            if len(line_lst) != 3:
                valid = True
                continue
            # get rid of status messages e.g. "* joe is now known as joe_lunch"
            if not line_lst[1].startswith('*'):
                irc_message = IRCMessage()
                # lets get time without square brackets
                time = line_lst[0][1:-1]
                message_date = format_time(date, time)
                irc_message.date = message_date
                # get rid of leading # especially due to html tabs, other signs
                # may cause troubles too though = FIXME
                while channel.startswith('#'):
                    channel = channel[1:]
                irc_message.irc_channel = channel
                # lets get nick without angle brackets
                nick = line_lst[1][1:-1]
                irc_message.nick = nick
                message_text = line_lst[2]
                irc_message.message = message_text
                message_list.append(irc_message)
                # add into DB in one transaction
                if len(message_list) == 120:
                    save_multiple_msgs(message_list)
                    message_list = []
        save_multiple_msgs(message_list)
        if valid:
            logger.info('Some line(s) not valid...')
            valid = False


class Command(BaseCommand):
    help = "Feed DB with IRC messages"

    def add_arguments(self, parser):
        parser.add_argument('-a', '--archive',
                            action='store_true',
                            default=False,
                            dest='archive',
                            help='Archive processed message files to consumed'
                                 'folder and delete it',
                            )

    def handle(self, *args, **options):
        channels = [chan_dir for chan_dir in os.listdir(MESSAGES)
                    if os.path.isdir(os.path.join(MESSAGES, chan_dir))]
        if not channels:
            logger.info('No channel dir in the messages folder...')
            return
        for channel in channels:
            channel_dir = os.path.join(MESSAGES, channel)
            pattern = '\d{4}-\d{2}-\d{2}.log$'
            log_fnames = [log_fname for log_fname in sorted(os.listdir(channel_dir))
                          if re.match(pattern, log_fname)]
            if not log_fnames:
                logger.info('There are no messages to consume in {}...'.format(channel))
                continue
            for log_fname in log_fnames:
                log_path = os.path.join(channel_dir, log_fname)
                into_db(log_path, channel)
                if options['archive']:
                    archive_log_file(log_path, channel_dir)
