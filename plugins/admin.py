# -*- coding: utf-8 -*-

from stdPlugin import stdPlugin

class admin(stdPlugin):

    events = [('pubmsg', {'priority': 0, 'exclusive': True, 'command_namespace': 'admin'})]
    admins = ['Gordon']

    def on_cmd(self, serv, ev, command, args):
        sender = ev.source().split('!')[0]
        if command == 'quit':
            if sender in self.admins:
                self.bot.die()
