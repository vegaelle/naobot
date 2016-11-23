# -*- coding: utf-8 -*-

import random

from irc3.plugins.command import command
from irc3.plugins.cron import cron
import irc3

from .lib.markov import Markov


@irc3.plugin
class Learn:
    """Apprend continuellement les mots utilisés sur un canal, et génère des
    phrases aléatoires et stupides.
    """

    markov = Markov()

    def __init__(self, bot):
        self.bot = bot
        for chan in self.bot.channels:
            self.get_dico(chan)

    def parse(self, chan, message):
        self.markov.add_sentence(chan, message)
        self.save_dico(chan)

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_privmsg(self, mask=None, event=None, target=None, data=None, **kw):
        if not data.startswith(self.bot.config.get('irc3.plugins.command', {})
                               .get('cmd', '!')):
            self.parse(target, data)

    @irc3.event(irc3.rfc.JOIN)
    def on_join(self, mask, channel, **kwargs):
        if mask.nick == self.bot.nick:
            self.get_dico(channel)

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
        for chan in self.bot.channels:
            if random.randint(1, 100) < 10:
                self.bot.privmsg(chan, self.markov.
                                 get_sentence(chan))
            self.bot.write_config(chan, self.bot.get_config(chan))

    @irc3.extend
    def write_config(self, target, data):
        if 'learn' not in self.bot.db:
            self.bot.db['learn'] = {}
            self.bot.db['learn'][target] = data

    @irc3.extend
    def get_config(self, target, default=None):
        if 'learn' not in self.bot.db:
            return default if default is not None else {}
        else:
            if target not in self.bot.db['learn']:
                return default if default is not None else {}
            return self.bot.db['learn'][target]
