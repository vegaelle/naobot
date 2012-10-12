# -*- coding: utf-8 -*-

import inspect
from stdPlugin import stdPlugin

class help(stdPlugin):

    events = {'pubmsg': {'priority': 6, 'exclusive': True, 'command_namespace': 'help'}}

    def on_cmd(self, serv, ev, command, args, helper):
        if command == '':
            plugin_list = ', '.join(self.bot.registered_plugins.keys())
            serv.privmsg(helper['target'], u'Pour obtenir l’aide d’un plugin, tapez %shelp <plugin>' % self.bot.conf['command_prefix'])
            serv.privmsg(helper['target'], u'Liste des plugins actifs : %s' % plugin_list)
            return True
        elif command in self.bot.registered_plugins.keys():
            command_help = inspect.getdoc(self.bot.registered_plugins[command])
            serv.privmsg(helper['target'], u'Documentation de la commande %s%s :' % (self.bot.conf['command_prefix'], command))
            serv.privmsg(helper['target'], command_help)
            return True
        else:
            serv.privmsg(helper['target'], u'Commande inconnue. Tapez %shelp pour une liste des plugins' % self.bot.conf['command_prefix'])
            return True

