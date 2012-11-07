# -*- coding: utf-8 -*-

from pyfiglet import Figlet
from stdPlugin import stdPlugin

class figlet(stdPlugin):
    u'''Écrit en mode figlet, qui a pour principal intérêt de flooder un canal.'''

    events = {'pubmsg': {'exclusive': True, 'command_namespace': 'figlet'}}
    width = 80 # max nb of characters per line

    def on_cmd(self, serv, ev, command, args, helper):
        u'''%(namespace)s <text> : écrit le texte donné en figlet. Ne gère que les caractères ASCII.'''
        f = Figlet()
        args.insert(0, command)
        message = ' '.join(args)
        figlet_msg = {}
        figlet_width = 0
        for c in message:
            figlet_c = f.renderText(c).split('\n')
            added_width = max(len(fc) for fc in figlet_c)
            # adding this character will make a too long line
            if figlet_width + added_width > self.width:
                # flush figlet message
                self.privfigletmsg(serv, helper['target'], figlet_msg)
                figlet_msg = {}
                figlet_width = 0
            # adding the character
            l = 0
            for fc in figlet_c:
                figlet_msg[l] = figlet_msg.get(l, '') + fc
                l += 1
            figlet_width += added_width
        # flush figlet message
        self.privfigletmsg(serv, helper['target'], figlet_msg)


    def privfigletmsg(self, serv, target, figletmsg):
        """
        Send the figlet message, removing blank lines
        """
        for l in xrange(7): # Figlet returns a 7-line message
            msg = figletmsg[l].rstrip() # remove trailing spaces
            if msg: # do not print empty lines
                serv.privmsg(target, msg)
