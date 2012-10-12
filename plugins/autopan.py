# -*- coding: utf-8 -*-

from stdPlugin import stdPlugin

class autopan(stdPlugin):

    events = {'pubmsg': {'priority': 2, 'exclusive': True}}

    targets = (
            ('coin', 'pan'),
            ('nioc', 'nap'),
            ('\_o<', '\_x<'),
            ('>o_/', '>x_/'),
            (u'ᴎIOↃ', u'ᴎAP'),
            ('koin', 'pang'),
        )

    def on_pubmsg(self, serv, ev, helper):
        pans = []
        for coin, pan in self.targets:
            for _ in xrange(helper['message'].count(coin)):
                pans.append(pan)
        if pans:
            if len(pans) < 3:
                serv.privmsg(helper['target'], ' '.join(pans))
                return True
            else:
                serv.privmsg(helper['target'], 'raaa' + 'ta' * len(pans))
                return True
