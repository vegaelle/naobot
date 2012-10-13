# -*- coding: utf-8 -*-

from pyfiglet import Figlet
from stdPlugin import stdPlugin

class figlet(stdPlugin):
    u'''Écrit en mode figlet, qui a pour principal intérêt de flooder un canal.'''

    events = {'pubmsg': {'priority': 4, 'exclusive': True, 'command_namespace': 'figlet'}}

    def on_cmd(self, serv, ev, command, args, helper):
        u'''%(namespace)s <text> : écrit le texte donné en figlet. Ne gère que les caractères ASCII.'''
        f = Figlet()
        args.insert(0, command)
        message = ' '.join(args)
        for line in f.renderText(message).split('\n'):
            line = line.rstrip() # remove trailing spaces
            if line: # do not print empty lines
                serv.privmsg(helper['target'], line)
