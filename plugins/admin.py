# -*- coding: utf-8 -*-

import sys
from stdPlugin import stdPlugin


class admin(stdPlugin):
    u'''Permet d’administrer le bot. Les commandes, sauf mention contraire,
    sont réservées aux administrateurs.
    '''

    events = {'pubmsg': {'exclusive': True, 'command_namespace': 'sudo'},
              'privmsg': {'exclusive': True, 'command_namespace': 'sudo'},
              }

    def is_admin(self, nick):
        sender = nick.split('!')[0]
        if sender in self.conf['admins']:
            return True
        else:
            return False

    def on_cmd(self, serv, ev, command, args, helper):
        u'''%(namespace)s quit : termine sauvagement le bot.
        %(namespace)s list : indique les plugins activés.
        %(namespace)s load <plugin> (<priorité>) : charge et active un plugin,
            en lui assignant optionnellement une priorité donnée.
        %(namespace)s unload <plugin> : désactive un plugin.
        %(namespace)s reload <plugin> : recharge un plugin, s’il a été modifié'
        %(namespace)s reload-all : recharge tous les plugins actifs, s’ils ont
            été modifiés'
        %(namespace)s join <chan> : rejoint un canal.
        %(namespace)s leave <chan> : quitte un canal.
        %(namespace)s chans : indique la liste des canaux actifs.'''
        if not self.is_admin(ev.source):
            serv.privmsg(helper['target'], u'Nope.')
            return True
        if command == 'quit':
            self.bot.die()
            return True
        elif command == 'list':
            plugin_list = ', '.join(self.bot.registered_plugins.keys())
            serv.privmsg(helper['target'], u'Plugins chargés : %s' %
                         plugin_list)
        elif command == 'load':
            if len(args) == 2:
                result = self.bot.load_plugin(args[0], args[1])
            else:
                result = self.bot.load_plugin(args[0])
            if result:
                serv.privmsg(helper['target'], u'Plugin %s chargé' % args[0])
                return True
            else:
                serv.privmsg(helper['target'], u'Erreur : impossible de '
                             + 'charger le plugin %s' % args[0])
                return True
        elif command == 'unload':
            if args[0] == 'admin':
                serv.privmsg(helper['target'], u'Erreur : impossible de '
                             + 'désactiver le plugin d’administration !')
                return False
            result = self.bot.unload_plugin(args[0])
            if result:
                serv.privmsg(helper['target'], u'Plugin %s désactivé' %
                             args[0])
                return True
            else:
                serv.privmsg(helper['target'], u'Erreur : le plugin %s est '
                             + 'introuvable ou inactif' % args[0])
                return True
        elif command == 'reload':
            try:
                reload(sys.modules['plugins.'+args[0]])
                self.bot.load_plugin(args[0])
                serv.privmsg(helper['target'], u'Plugin %s rechargé' % args[0])
            except KeyError:
                serv.privmsg(helper['target'], u'Erreur : le plugin %s est '
                             + 'introuvable ou inactif' % args[0])
            return False
        elif command == 'reload-all':
            try:
                for plugin in self.bot.registered_plugins:
                    reload(sys.modules['plugins.'+plugin])
                    self.bot.load_plugin(plugin)
                    serv.privmsg(helper['target'], u'Plugin %s rechargé' %
                                 args[0])
            except KeyError:
                serv.privmsg(helper['target'], u'Erreur : le plugin %s est '
                             + 'introuvable ou inactif' % plugin)
            return False
        elif command == 'join':
            chan_name = args[0]
            if not chan_name.startswith('#'):
                chan_name = '#%s' % chan_name
            result = serv.join(chan_name)
        elif command == 'leave':
            chan_name = args.pop(0)
            reason = ' '.join(args)
            if not chan_name.startswith('#'):
                chan_name = '#%s' % chan_name
            result = serv.part(chan_name, reason)
        elif command == 'chans':
            chanlist = []
            for chan in self.bot.channels.keys():
                chanlist.append(chan)
            serv.privmsg(helper['target'], u'Canaux actifs : %s' % ', '.
                         join(chanlist))
        elif command+' '+' '.join(args) == 'make me a sandwich':
            serv.privmsg(helper['target'], 'What? Go make it yourself!')
            return True
        else:
            serv.privmsg(helper['target'], 'Commande %s inconnue' % command)
