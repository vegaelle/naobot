# -*- coding: utf-8 -*-

import re

class stdPlugin(object):

    #events = {'pubmsg': {'priority': 9999, 'exclusive': True, 'command_namespace': 'say'}}
    events = {}

    def __init__(self, bot, conf):
        self.bot = bot
        self.conf = conf

    def on_pubmsg(self, serv, ev, helper):
        return False

    def on_privmsg(self, serv, ev, helper):
        return False

    def on_action(self, serv, ev, helper):
        return False

    def on_join(self, serv, ev, helper):
        return False

    def on_kick(self, serv, ev, helper):
        return False

    def on_cmd(self, serv, ev, command, args, helper):
        return false

    def say(self, serv, target, message):
        if message.startswith('/me'):
            serv.action(target, message[3:])
        else:
            serv.privmsg(target, message)
