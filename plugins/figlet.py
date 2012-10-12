# -*- coding: utf-8 -*-

from pyfiglet import Figlet
from stdPlugin import stdPlugin

class figlet(stdPlugin):

    events = {'pubmsg': {'priority': 4, 'exclusive': True, 'command_namespace': 'figlet'}}

    def on_cmd(self, serv, ev, command, args, helper):
        f = Figlet()
        args.insert(0, command)
        message = ' '.join(args)
        for line in f.renderText(message).split('\n'):
            line = line.rstrip() # remove trailing spaces
            if line: # do not print empty lines
                serv.privmsg(helper['target'], line)
