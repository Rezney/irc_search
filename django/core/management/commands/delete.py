from django.core.management.base import BaseCommand
from core.models import IRCMessage

import logging

logger = logging.getLogger('django')


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
                            '-a', '--all',
                            action='store_true',
                            default=False,
                            dest='all',
                            help='Delete all messages!!!',
        )
        parser.add_argument(
                            '-c', '--channel',
                            action='store',
                            dest='channel',
                            help='Delete all messages for particular channel!',
        )

    def handle(self, *args, **options):
        if not options['all'] and not options['channel']:
            # Lame W/A
            logger.info('No option provided')
            return
        if options['all']:
            logger.info('Deleting all messages !!!')
            IRCMessage.objects.all().delete()
        if options['channel']:
            logger.info('Deleting messages for channel {}'.format(options['channel']))
            IRCMessage.objects.filter(irc_channel=options['channel']).delete()
