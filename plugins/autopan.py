# -*- coding: utf-8 -*-

import re
from stdPlugin import stdPlugin

class autopan(stdPlugin):

    events = [('pubmsg', {'priority': 1, 'exclusive': True})]

    def on_pubmsg(self, serv, ev, helper):
        if helper['message'].find('coin') >= 0:
            serv.privmsg(ev.target(), 'pan')
            return True
        elif helper['message'].find('nioc') >= 0:
            serv.privmsg(ev.target(), 'nap')
            return True
        if helper['message'].find('\_o<') >= 0:
            serv.privmsg(ev.target(), 'pan \_x<')
            return True
        if helper['message'].find('>o_/') >= 0:
            serv.privmsg(ev.target(), 'pan >x_/')
            return True

