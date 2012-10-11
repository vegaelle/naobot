# -*- coding: utf-8 -*-

from pyfiglet import Figlet
from stdPlugin import stdPlugin

class figlet(stdPlugin):

    events = {'pubmsg': {'priority': 3, 'exclusive': True, 'command_namespace': 'figlet'}}

    def __init__(self, bot, conf):
        self.bot = bot
        self.conf = conf

    def on_cmd(self, serv, ev, command, args, helper):
        f = Figlet()
        args = [command] + args
        message = ' '.join(args)
        for line in f.renderText(message).split('\n'):
            serv.privmsg(helper['target'], line)
