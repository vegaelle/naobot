# -*- coding: utf-8 -*-

from stdPlugin import stdPlugin

class autopan(stdPlugin):

    events = [('pubmsg', {'priority': 1, 'exclusive': True})]

    targets = (
            ('coin', 'pan'),
            ('nioc', 'nap'),
            ('\_o<', '\_x<'),
            ('>o_/', '>x_/'),
            (u'ᴎIOↃ', u'ᴎAP'),
        )

    def on_pubmsg(self, serv, ev, helper):
        for coin, pan in self.targets:
            if helper['message'].find(coin) >= 0:
                serv.privmsg(helper['target'], pan)
                # only trigger one time per msg
                return True
