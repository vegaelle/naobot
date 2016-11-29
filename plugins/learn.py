# -*- coding: utf-8 -*-

import random
import re

from irc3.plugins.command import command
from irc3.plugins.cron import cron
import irc3

from .lib.markov import Markov

URL_RE = r'(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]'\
    '\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d'\
    '|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9'\
    ']+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-'\
    'z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?'


@irc3.plugin
class Learn:
    """Apprend continuellement les mots utilisés sur un canal, et génère des
    phrases aléatoires et stupides.
    """

    markov = Markov()

    def __init__(self, bot):
        self.bot = bot
        self.quiet_chans = []
        self.is_last_speaker = {}
        if 'plugins.learn' in self.bot.config and 'quiet_channels' in\
                self.bot.config['plugins.learn']:
            self.quiet_chans = self.bot\
                .config['plugins.learn']['quiet_channels']
        for chan in self.bot.channels:
            self.get_dico(chan)
            self.is_last_speaker[chan] = False

    def parse(self, chan, message):
        # stripping URLs
        message = re.sub(URL_RE, '', message)
        self.markov.add_sentence(chan, message)
        self.save_dico(chan)

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_privmsg(self, mask=None, event=None, target=None, data=None, **kw):
        if target not in self.quiet_chans:
            if not data.startswith(
                    self.bot.config.get('irc3.plugins.command', {})
                        .get('cmd', '!')):
                self.parse(target, data)
                if self.bot.nick in data:
                    self.bot.privmsg(target, self.markov.
                                     get_sentence(target, mask.nick,
                                                  can_ignore=True))
                    self.is_last_speaker[target] = True
                else:
                    self.is_last_speaker[target] = False

    @irc3.event(irc3.rfc.JOIN)
    def on_join(self, mask, channel, **kwargs):
        if mask.nick == self.bot.nick:
            self.get_dico(channel)
            self.is_last_speaker[channel] = False

    @command(permission='view')
    def sentence(self, mask, target, args):
        """Sentence : génère une phrase aléatoire

            %%sentence [<mot>...]
        """
        if len(args['<mot>']) == 0:
            self.bot.privmsg(target,
                             self.markov.get_sentence(target))
        else:
            self.bot.privmsg(target,
                             self.markov.get_sentence(target,
                                                      ' '.join(args['<mot>'])))
        self.is_last_speaker[target] = True

    @command(permission='view')
    def stats(self, mask, target, args):
        """Stats : donne la taille du dictionnaire

            %%stats
        """
        self.bot.privmsg(target, 'Mot connus : %d'
                         % self.markov.get_stats(target))

    def get_dico(self, chan):
        data = self.bot.get_config(chan, self.markov.default_data())
        self.markov.load(chan, data)

    def save_dico(self, chan):
        data = self.markov.dump(chan)
        return self.bot.write_config(chan, data)

    @cron('* * * * *')
    @irc3.asyncio.coroutine
    def on_run(self):
        nonquiet_chans = [c for c in self.bot.channels if c not in
                          self.quiet_chans]
        for chan in nonquiet_chans:
            if not self.is_last_speaker[chan] and random.randint(1, 100) < 10:
                self.bot.privmsg(chan, self.markov.
                                 get_sentence(chan))
                self.is_last_speaker[chan] = True

    @irc3.extend
    def write_config(self, target, data):
        if 'learn' not in self.bot.db:
            self.bot.db['learn.{}'.format(target)] = {}
        self.bot.db['learn.{}'.format(target)] = data

    @irc3.extend
    def get_config(self, target, default=None):
        if 'learn.{}'.format(target) not in self.bot.db:
            return default if default is not None else {}
        else:
            return self.bot.db['learn.{}'.format(target)]
