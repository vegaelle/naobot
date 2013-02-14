# -*- coding: utf-8 -*-

from stdPlugin import stdPlugin

class autopan(stdPlugin):
    u'''Réagit pragmatiquement aux invasions palmipèdes sur les canaux.'''

    events = {'pubmsg': {'exclusive': True}}

    targets = (
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
        pans = []
        for coin, pan in self.targets:
            for _ in xrange(helper['message'].lower().count(coin)):
                pans.append(pan)
        if pans:
            if len(pans) < 3:
                serv.privmsg(helper['target'], ' '.join(pans))
                return True
            else:
                serv.privmsg(helper['target'], 'raaa' + 'ta' * len(pans))
                return True
