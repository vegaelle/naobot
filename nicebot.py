# -*- coding: utf-8 -*-

import sys
import os
import argparse
from irc import bot

#from settings import conf, plugins_conf

class Nicebot(bot.SingleServerIRCBot):

    registered_plugins = {}
    events = {}

    def __init__(self, conf, plugins_conf):
        self.conf = conf
        bot.SingleServerIRCBot.__init__(self, self.conf['server'], self.conf['nick'], self.conf['fullname'])
        for plugin_name in self.conf['plugins']:
            self.load_plugin(plugin_name)

    def load_plugin(self, plugin_name):
        try:
            importStr = 'from plugins import %s' % plugin_name
            exec importStr
            plugin = getattr(sys.modules['plugins.'+plugin_name], plugin_name)
            try:
                plugin_conf = plugins_conf[plugin_name]
            except KeyError:
                plugin_conf = {}
            self.registered_plugins[plugin_name] = plugin(self, plugin_conf)
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
            return False
        except:
            print 'Error while loading plugin %s' % plugin_name
            return False
        return True

    def unload_plugin(self, plugin_name):
        try:
            del self.registered_plugins[plugin_name]
            for i in range(len(self.events)):
                if self.events[i]['plugin'] == plugin_name:
                    del self.events[i]
            return True
        except IndexError:
            return False

    def on_welcome(self, serv, ev):
        try:
            self.conf['password']
            try:
                self.conf['login_command']
                login_command = self.conf['login_command']
            except KeyError:
                login_command = ('NickServ', 'identify %s')
            serv.privmsg(login_command[0], login_command[1] % self.conf['password'])
        except KeyError:
            pass
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
                        try:
                            answered = answered or self.registered_plugins[plugin_event['plugin']].on_pubmsg(serv, ev, helper)
                        except KeyError: # si on désactive le plugin, ça n’arrête pas la boucle
                            pass
        except AssertionError:
            pass

    def on_action(self, serv, ev):
        message = ev.arguments()[0]
        sender = ev.source().split('!')[0]
        chan = self.channels[ev.target()]
        helper = {'message': message, 'sender': sender, 'chan': chan}
        try:
            assert isinstance(self.events['action'], dict)
            answered = False
            for key in sorted(self.events['action'].iterkeys()):
                plugin_event = self.events['action'][key]
                if not plugin_event['exclusive'] or not answered:
                    answered = answered or self.registered_plugins[plugin_event['plugin']].on_action(serv, ev, helper)
        except AssertionError:
            pass

    def on_join(self, serv, ev):
        chan = self.channels[ev.target()]
        sender = ev.source().split('!')[0]
        helper = {'sender': sender, 'chan': chan}
        try:
            assert isinstance(self.events['join'], dict)
            answered = False
            for key in sorted(self.events['join'].iterkeys()):
                plugin_event = self.events['join'][key]
                if not plugin_event['exclusive'] or not answered:
                    answered = answered or self.registered_plugins[plugin_event['plugin']].on_join(serv, ev, helper)
        except AssertionError:
            pass

    def on_kick(self, serv, ev):
        victim = ev.arguments()[0]
        message = ev.arguments()[1]
        sender = ev.source().split('!')[0]
        chan = self.channels[ev.target()]
        helper = {'message': message, 'sender': sender, 'chan': chan, 'victim': victim}
        try:
            assert isinstance(self.events['kick'], dict)
            answered = False
            for key in sorted(self.events['kick'].iterkeys()):
                plugin_event = self.events['kick'][key]
                if not plugin_event['exclusive'] or not answered:
                    answered = answered or self.registered_plugins[plugin_event['plugin']].on_kick(serv, ev, helper)
        except AssertionError:
            pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Nicelab IRC bot', version='%(prog)s 0.5')
    parser.add_argument('-d', '--daemon', action='store_true', default=False, dest='daemon', help='start bot as a daemon')
    parser.add_argument('-c', '--config-file', action='store', dest='config_file', default='settings', help='use given file in ./settings/ dir for bot configuration')

    results = parser.parse_args()

    if results.daemon:
        try:
            pid = os.fork()
        except OSError, e:
            raise Exception, '%s [%d]' % (e.strerror, e.errno)

        if pid == 0:
            os.setsid()
            try:
                pid = os.fork()
            except OSError, e:
                raise Exception, '%s [%d]' % (e.strerror, e.errno)

            if pid == 0:
                pass
            else:
                os._exit(0)
        else:
            os._exit(0)

    exec('from settings.%s import conf, plugins_conf' % results.config_file)

    Nicebot(conf, plugins_conf).start()
