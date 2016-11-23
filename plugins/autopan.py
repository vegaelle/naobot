# -*- coding: utf-8 -*-

import re

from irc3.plugins.command import command
import irc3

# From http://stackoverflow.com/a/3009124


def case_sensitive_replace(s, before, after):
    """Replaces 'before' by 'after' in 's'. Matching is case-insensitive,
    but the replaced string keeps the original case of the matched
    part. Note that 'after' MUST be shorter than 'before'."""
    regex = re.compile(re.escape(before), re.I | re.U)
    return regex.sub(lambda x: ''.join(d.upper() if c.isupper() else d.lower()
                                       for c, d in zip(x.group(), after)), s)


@irc3.plugin
class Autopan:
    u'''Réagit pragmatiquement aux invasions palmipèdes sur les canaux.'''

    events = {'pubmsg': {'exclusive': True},
              'action': {'exclusive': True}}

    targets = (
        # Must not overlap
        ('coin', 'pan'),
        ('nioc', 'nap'),
        ('\_o<', '\_x<'),
        ('>o_/', '>x_/'),
        (u'ᴎIOↃ', u'ᴎAP'),
        ('koin', 'pang'),
        ('c01n', 'p4n'),
        ('n10c', 'n4p'),
        )

    def __init__(self, bot):
        self.bot = bot

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_privmsg(self, mask=None, event=None, target=None, data=None, **kw):
        words = re.findall(r"[\w'<>/\\-]+", data, re.U)
        output = []
        for w in words:
            tmp = w
            for coin, pan in self.targets:
                tmp = case_sensitive_replace(tmp, coin, pan)
            # If the word has been modified
            if tmp != w:
                output.append(tmp)
        # Print all those words
        if len(output) > 0:
            self.bot.privmsg(target, ' '.join(output))
