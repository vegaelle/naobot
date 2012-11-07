# -*- coding: utf-8 -*-

import inspect
from stdPlugin import stdPlugin

class help(stdPlugin):
    u'''Indique le fonctionnement des divers plugins et commandes.'''

    events = {'pubmsg': {'exclusive': True, 'command_namespace': 'help'},
              'privmsg': {'exclusive': True, 'command_namespace': 'help'}}

    def on_cmd(self, serv, ev, command, args, helper):
        u'''%(namespace)s : liste les plugins disponibles.
        %(namespace)s <plugin> : indique l’aide du plugin donné.'''
        if command == '':
            plugin_list = ', '.join(self.bot.registered_plugins.keys())
            serv.privmsg(helper['target'], u'Pour obtenir l’aide d’un plugin, tapez %shelp <plugin>' % self.bot.conf['command_prefix'])
            serv.privmsg(helper['target'], u'Liste des plugins actifs : %s' % plugin_list)
            return True
        elif command in self.bot.registered_plugins.keys():
            plugin_help = inspect.getdoc(self.bot.registered_plugins[command])
            serv.privmsg(helper['target'], u'Documentation du plugin %s :' % command)
            serv.privmsg(helper['target'], '\t\t'+plugin_help)
            try:
                command_help = inspect.getdoc(getattr(self.bot.registered_plugins[command], 'on_cmd')).split('\n')
                command_namespace = self.bot.registered_plugins[command].events[ev.eventtype()]['command_namespace']
                serv.privmsg(helper['target'], u'Liste des commandes :')
                for line in command_help:
                    serv.privmsg(helper['target'], '\t\t'+line % {'namespace': self.bot.conf['command_prefix']+command_namespace})
            except AttributeError:
                serv.privmsg(helper['target'], u'Le plugin ne dispose d’aucune commande.')
            return True
        else:
            serv.privmsg(helper['target'], u'Commande inconnue. Tapez %shelp pour une liste des plugins' % self.bot.conf['command_prefix'])
            return True

