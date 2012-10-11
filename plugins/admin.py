# -*- coding: utf-8 -*-

from stdPlugin import stdPlugin

class admin(stdPlugin):

    events = {
            'pubmsg': {'priority': 0, 'exclusive': True, 'command_namespace': 'sudo'},
            'privmsg': {'priority': 0, 'exclusive': True, 'command_namespace': 'sudo'},
        }

    def on_cmd(self, serv, ev, command, args, helper):
        sender = ev.source().split('!')[0]
        if command == 'quit':
            if sender in self.conf['admins']:
                self.bot.die()
                return True
        elif command == 'list':
            if sender in self.conf['admins']:
                plugin_list = ', '.join(self.bot.registered_plugins.keys())
                serv.privmsg(helper['target'], u'Plugins chargés : %s' % plugin_list)
        elif command == 'load':
            if sender in self.conf['admins']:
                result = self.bot.load_plugin(args[0])
                if result:
                    serv.privmsg(helper['target'], u'Plugin %s chargé' % args[0])
                    return True
                else:
                    serv.privmsg(helper['target'], u'Erreur : impossible de charger le plugin %s' % args[0])
                    return True
        elif command == 'unload':
            if sender in self.conf['admins']:
                if args[0] == 'admin':
                    serv.privmsg(helper['target'], u'Erreur : impossible de désactiver le plugin d’administration !')
                    return False
                result = self.bot.unload_plugin(args[0])
                if result:
                    print u'Plugin %s désactivé' % args[0]
                    serv.privmsg(helper['target'], u'Plugin %s désactivé' % args[0])
                    return True
                else:
                    print u'Erreur : le plugin %s est introuvable ou inactif' % args[0]
                    serv.privmsg(helper['target'], u'Erreur : le plugin %s est introuvable ou inactif' % args[0])
                    return True
        elif command == 'join':
            if sender in self.conf['admins']:
                chan_name = args[0]
                if not chan_name.startswith('#'):
                    chan_name = '#%s' % chan_name
                result = serv.join(chan_name)
        elif command == 'leave':
            if sender in self.conf['admins']:
                chan_name = args.pop(0)
                reason = ' '.join(args)
                if not chan_name.startswith('#'):
                    chan_name = '#%s' % chan_name
                result = serv.part(chan_name, reason)
        else:
            serv.privmsg(helper['target'], 'Commande %s inconnue' % command)
