# -*- coding: utf-8 -*-

import re
from stdPlugin import stdPlugin

class autopan(stdPlugin):

    events = [('pubmsg', {'priority': 1, 'exclusive': True})]

    def on_pubmsg(self, serv, ev, helper):
        if helper['message'].find('coin') >= 0:
            serv.privmsg(helper['target'], 'pan')
            return True
        elif helper['message'].find('nioc') >= 0:
            serv.privmsg(helper['target'], 'nap')
            return True
        if helper['message'].find('\_o<') >= 0:
            serv.privmsg(helper['target'], 'pan \_x<')
            return True
        if helper['message'].find('>o_/') >= 0:
            serv.privmsg(helper['target'], 'pan >x_/')
            return True
        if helper['message'].find(u'ᴎIOↃ') >= 0:
            serv.privmsg(helper['target'], u'ᴎAP')
            return True

