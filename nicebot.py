# -*- coding: utf-8 -*-

import sys
from irc import bot

conf = {'server': [('irc.geeknode.org', 6667)],
        'nick': 'Nicebot',
        'fullname': 'Le bot IRC du Nicelab',
        'chans': ['#poney-gonflable'],
        'command_prefix': '~',
        'plugins': ['admin', 'autopan', 'catcopter', 'discuss']}

class Nicebot(bot.SingleServerIRCBot):

    registered_plugins = {}
    events = {}

    def __init__(self):
        bot.SingleServerIRCBot.__init__(self, conf['server'], conf['nick'], conf['fullname'])
        for plugin_name in conf['plugins']:
            try:
                importStr = 'from plugins import %s' % plugin_name
                exec importStr
                plugin = getattr(sys.modules['plugins.'+plugin_name], plugin_name)
                self.registered_plugins[plugin_name] = plugin(self)
                for e in plugin.events:
                    try:
                        try:
                            self.events[e[0]]
                            assert isinstance(self.events[e[0]], dict)
                        except KeyError:
                            self.events[e[0]] = {}
                    except AssertionError:
                        self.events[e[0]] = {}
                    e[1]['plugin'] = plugin_name
                    self.events[e[0]][int(e[1]['priority'])] = e[1]
            except ImportError:
                print 'Unable to load plugin %s' % plugin_name
            #except:
            #    print 'Error while loading plugin %s' % plugin_name

    def on_welcome(self, serv, ev):
        for c in conf['chans']:
            serv.join(c)

    def on_pubmsg(self, serv, ev):
        message = ev.arguments()[0]
        sender = ev.source().split('!')[0]
        chan = self.channels[ev.target()]
        helper = {'message': message, 'sender': sender, 'chan': chan}
        try:
            assert isinstance(self.events['pubmsg'], dict)
            answered = False
            for key in sorted(self.events['pubmsg'].iterkeys()):
                plugin_event = self.events['pubmsg'][key]
                if message.startswith(conf['command_prefix']):
                    try:
                        plugin_event['command_namespace']
                        if message.startswith(conf['command_prefix']+plugin_event['command_namespace']):
                            # on appelle une commande
                            cmd_len = len(conf['command_prefix']+plugin_event['command_namespace']+' ')
                            message = message[cmd_len:]
                            args = message.split(' ')
                            args.reverse()
                            command = args.pop()
                            args.reverse()
                            answered = self.registered_plugins[plugin_event['plugin']].on_cmd(serv, ev, command, args)
                    except KeyError:
                        pass
                else:
                    if not plugin_event['exclusive'] or not answered:
                        answered = answered or self.registered_plugins[plugin_event['plugin']].on_pubmsg(serv, ev, helper)
        except AssertionError:
            pass

if __name__ == '__main__':
    Nicebot().start()
