# -*- coding: utf-8 -*-

import re

from stdPlugin import stdPlugin

class autopan(stdPlugin):
    u'''Réagit pragmatiquement aux invasions palmipèdes sur les canaux.'''

    events = {'pubmsg': {'exclusive': True}}

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

    def on_pubmsg(self, serv, ev, helper):
        words = re.findall(r"[\w'<>/\\]+", helper['message'], re.U)
        output = []
        for w in words:
            tmp = w
            for coin, pan in self.targets:
                tmp = tmp.replace(coin, pan)
            # If the word has been modified
            if tmp != w:
                output.append(tmp)
        # Print all those words
        if len(output) > 0:
            serv.privmsg(helper['target'], ' '.join(output))
        return True
