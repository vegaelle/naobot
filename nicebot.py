# -*- coding: utf-8 -*-

import sys
from irc import bot

conf = {'server': [('irc.geeknode.org', 6667)],
        'nick': 'Nicebot',
        'fullname': 'Le bot IRC du Nicelab',
        'chans': ['#poney-gonflable'],
        'plugins': ['discuss']}

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
                self.registered_plugins[plugin_name] = plugin()
                for e in plugin.events:
                    try:
                        try:
                            self.events[e[0]]
                            assert isinstance(self.events[e[0]], list)
                        except KeyError:
                            self.events[e[0]] = {}
                    except AssertionError:
                        self.events[e[0]] = {}
                    e[1]['plugin'] = plugin_name
                    self.events[e[0]][int(e[1]['priority'])] = e
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
                plugin_conf = plugin_event[1]
                if not plugin_conf['exclusive'] or not answered:
                    answered = answered or self.registered_plugins[plugin_event[1]['plugin']].on_pubmsg(serv, ev, helper)
        except AssertionError:
            pass

if __name__ == '__main__':
    Nicebot().start()
