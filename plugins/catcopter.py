# -*- coding: utf-8 -*-

from stdPlugin import stdPlugin

class catcopter(stdPlugin):

    events = {'pubmsg': {'priority': 2, 'exclusive': True, 'command_namespace': 'catcopter'}}

    def on_cmd(self, serv, ev, command, args, helper):
        serv.privmsg(helper['target'], '''              ,-----.             ''')
        serv.privmsg(helper['target'], '''  __ __      ' |\=/| '      __ __ ''')
        serv.privmsg(helper['target'], '''    |        | /x x\ |        |   ''')
        serv.privmsg(helper['target'], '''    x--------.=\_Y_/=,--------x   ''')
        serv.privmsg(helper['target'], '''              .__U__,             ''')
        return True
