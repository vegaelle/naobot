# -*- coding: utf-8 -*-

import sys
import os
import argparse
import re
import pickle
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
            if not re.match('^[a-z]*$', plugin_name):
                raise Exception('Invalid plugin name')
            importStr = 'from plugins import %s' % plugin_name
            exec importStr
            plugin = getattr(sys.modules['plugins.'+plugin_name], plugin_name)
            if plugin_name in plugins_conf:
                plugin_conf = plugins_conf[plugin_name]
            else:
                plugin_conf = {}
            self.registered_plugins[plugin_name] = plugin(self, plugin_conf)
            for e_name, e_values in plugin.events.items():
                if e_name not in self.events:
                    self.events[e_name] = {}
                try:
                    assert isinstance(self.events[e_name], dict)
                except AssertionError:
                    self.events[e_name] = {}
                e_values['plugin'] = plugin_name
                self.events[e_name][int(e_values['priority'])] = e_values
        except (ImportError, Exception), e:
            print 'Unable to load plugin %s: %s' % (plugin_name, e.message)
            return False
        except Exception, e:
            print 'Error while loading plugin %s: %s' % (plugin_name, e.message)
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
        helper = {'message': ev.arguments()[0],
                  'sender': ev.source().split('!')[0],
                  'chan': self.channels[ev.target()],
                  'target': ev.target()
                 }
        try:
            assert isinstance(self.events['pubmsg'], dict)
            answered = False
            for key in sorted(self.events['pubmsg'].iterkeys()):
                plugin_event = self.events['pubmsg'][key]
                if helper['message'].startswith(conf['command_prefix']):
                    try:
                        plugin_event['command_namespace']
                        command_call = conf['command_prefix']+plugin_event['command_namespace']
                        if helper['message'].lower().startswith(command_call+' ') or helper['message'].lower() == command_call:
                            # on appelle une commande
                            cmd_len = len(conf['command_prefix']+plugin_event['command_namespace']+' ')
                            message = helper['message']
                            helper['message'] = helper['message'][cmd_len:]
                            args = helper['message'].split(' ')
                            command = args.pop(0).lower()
                            answered = self.registered_plugins[plugin_event['plugin']].on_cmd(serv, ev, command, args, helper)
                            helper['message'] = message
                    except KeyError, e:
                        pass
                else:
                    if not plugin_event['exclusive'] or not answered:
                        try:
                            answered = answered or self.registered_plugins[plugin_event['plugin']].on_pubmsg(serv, ev, helper)
                        except KeyError, e: # si on désactive le plugin, ça n’arrête pas la boucle
                            print '%s: %s' % (e.__class__.__name__, e.message)
        except (AssertionError, KeyError), e:
            print '%s: %s' % (e.__class__.__name__, e.message)

    def on_privmsg(self, serv, ev):
        helper = {'message': ev.arguments()[0],
                  'sender': ev.source().split('!')[0],
                  'target': ev.source().split('!')[0]
                 }
        try:
            assert isinstance(self.events['privmsg'], dict)
            answered = False
            for key in sorted(self.events['privmsg'].iterkeys()):
                plugin_event = self.events['privmsg'][key]
                if helper['message'].startswith(conf['command_prefix']):
                    try:
                        plugin_event['command_namespace']
                        command_call = conf['command_prefix']+plugin_event['command_namespace']
                        if helper['message'].lower().startswith(command_call+' ') or helper['message'].lower() == command_call:
                            # on appelle une commande
                            cmd_len = len(conf['command_prefix']+plugin_event['command_namespace']+' ')
                            helper['message'] = helper['message'][cmd_len:]
                            args = helper['message'].split(' ')
                            command = args.pop(0).lower()
                            answered = self.registered_plugins[plugin_event['plugin']].on_cmd(serv, ev, command, args, helper)
                    except KeyError:
                        pass
                else:
                    if not plugin_event['exclusive'] or not answered:
                        try:
                            answered = answered or self.registered_plugins[plugin_event['plugin']].on_privmsg(serv, ev, helper)
                        except KeyError: # si on désactive le plugin, ça n’arrête pas la boucle
                            pass
        except (AssertionError, KeyError):
            pass

    def on_action(self, serv, ev):
        helper = {'message': ev.arguments()[0],
                  'sender': ev.source().split('!')[0],
                  'chan': self.channels[ev.target()],
                  'target': ev.target()
                 }
        try:
            assert isinstance(self.events['action'], dict)
            answered = False
            for key in sorted(self.events['action'].iterkeys()):
                plugin_event = self.events['action'][key]
                if not plugin_event['exclusive'] or not answered:
                    answered = answered or self.registered_plugins[plugin_event['plugin']].on_action(serv, ev, helper)
        except (AssertionError, KeyError):
            pass

    def on_join(self, serv, ev):
        helper = {'chan': self.channels[ev.target()],
                  'sender': ev.source().split('!')[0],
                  'target': ev.target()
                 }
        try:
            assert isinstance(self.events['join'], dict)
            answered = False
            for key in sorted(self.events['join'].iterkeys()):
                plugin_event = self.events['join'][key]
                if not plugin_event['exclusive'] or not answered:
                    answered = answered or self.registered_plugins[plugin_event['plugin']].on_join(serv, ev, helper)
        except AssertionError, KeyError:
            pass

    def on_kick(self, serv, ev):
        helper = {'victim': ev.arguments()[0],
                  'message': ev.arguments()[1],
                  'sender': ev.source().split('!')[0],
                  'chan': self.channels[ev.target()],
                  'target': ev.target(),
                 }
        try:
            assert isinstance(self.events['kick'], dict)
            answered = False
            for key in sorted(self.events['kick'].iterkeys()):
                plugin_event = self.events['kick'][key]
                if not plugin_event['exclusive'] or not answered:
                    answered = answered or self.registered_plugins[plugin_event['plugin']].on_kick(serv, ev, helper)
        except (AssertionError, KeyError):
            pass

    def get_config(self, plugin, name, default=None):
        try:
            path = os.path.join('data', plugin.__class__.__name__)
            try:
                os.makedirs(path)
            except OSError:
                pass
            with open(os.path.join(path, name), 'rb') as data_file:
                data = pickle.load(data_file)
                return data
        except (OSError, IOError):
            return default

    def write_config(self, plugin, name, data):
        try:
            path = os.path.join('data', plugin.__class__.__name__)
            try:
                os.makedirs(path)
            except OSError:
                pass
            with open(os.path.join(path, name), 'wb') as data_file:
                pickle.dump(data, data_file)
                return True
        except (OSError, IOError):
            return False

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
