# -*- coding: utf-8 -*-


class PluginError(Exception):
    pass


class stdPlugin(object):
    u'''Permet de créer des plugins.'''

    # events = {'pubmsg': {'exclusive': True, 'command_namespace': 'say'}}
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
        u'''Retourne l’aide correspondant à chaque commande.'''
        return False

    def say(self, serv, target, message):
        if message.startswith('/me '):
            serv.action(target, message[4:])
        else:
            serv.privmsg(target, message)
