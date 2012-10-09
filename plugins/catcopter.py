# -*- coding: utf-8 -*-

from stdPlugin import stdPlugin

class catcopter(stdPlugin):

    events = [('pubmsg', {'priority': 2, 'exclusive': True, 'command_namespace': 'catcopter'})]

    def on_cmd(self, serv, ev, command, args):
        serv.privmsg(ev.target(), '''              ,-----.             ''')
        serv.privmsg(ev.target(), '''  __ __      ' |\=/| '      __ __ ''')
        serv.privmsg(ev.target(), '''    |        | /x x\ |        |   ''')
        serv.privmsg(ev.target(), '''    x--------.=\_Y_/=,--------x   ''')
        serv.privmsg(ev.target(), '''              .__U__,             ''')
        return True
