#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import re
import pickle
import datetime
import random
from irc import bot
from plugins.stdPlugin import PluginError

#from settings import conf, plugins_conf

class Nicebot(bot.SingleServerIRCBot):

    registered_plugins = {}
    events = {}

    colors = {'white': 0,
              'black': 1,
              'blue': 2,
              'green': 3,
              'red': 4,
              'brown': 5,
              'purple': 6,
              'orange': 7,
              'yellow': 8,
              'lightgreen': 9,
              'teal': 10,
              'lightcyan': 11,
              'lightblue': 12,
              'pink': 13,
              'grey': 14,
              'lightgrey': 15
              }
    color_char = '\x03%s'
    background_color_char = '%s,%s'
    bold_char = '\x02'
    reset_char = '\x15'

    def __init__(self, conf, plugins_conf, config_name):
        self.conf = conf
        self.config_name = config_name
        bot.SingleServerIRCBot.__init__(self, self.conf['server'], self.conf['nick'], self.conf['fullname'])
        self.runs = {}
        for plugin_name in self.conf['plugins']:
            self.load_plugin(plugin_name)

        #if isinstance(self.events['run'], list):
        #    for chan_name in self.conf['chans']:
        #        self.runs[chan_name] = {}
        #        for plugin_event in self.events['run']:
        #            if isinstance(plugin_event['frequency'], tuple):
        #                self.runs[chan_name][plugin_event['plugin']] = datetime.datetime.now() +\
        #                    datetime.timedelta(0, random.randint(*plugin_event['frequency']))
        #            else:
        #                self.runs[chan_name][plugin_event['plugin']] = datetime.datetime.now() +\
        #                    datetime.timedelta(0, plugin_event['frequency'])

    def load_plugin(self, plugin_name, priority=None):
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
                    self.events[e_name] = []
                try:
                    assert isinstance(self.events[e_name], list)
                except AssertionError:
                    self.events[e_name] = []
                e_values['plugin'] = plugin_name
                plugin_index = dict((p['plugin'], i) for i, p in enumerate(self.events[e_name]))
                try:
                    plugin_index[plugin_name]
                    self.events[e_name][plugin_index[plugin_name]] = e_values
                except KeyError:
                    if not priority:
                        self.events[e_name].append(e_values)
                    else:
                        self.events[e_name].insert(int(priority), e_values)
                if e_name == 'run':
                    for chan_name in self.conf['chans']:
                        if chan_name not in self.runs:
                            self.runs[chan_name] = {}
                        if isinstance(e_values['frequency'], tuple):
                            self.runs[chan_name][plugin_name] = datetime.datetime.now() +\
                                datetime.timedelta(0, random.randint(*e_values['frequency']))
                        else:
                            self.runs[chan_name][plugin_name] = datetime.datetime.now() +\
                                datetime.timedelta(0, e_values['frequency'])

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
            for name, ev in self.events.items():
                to_del = []
                for i in range(len(ev)):
                    if ev[i]['plugin'] == plugin_name:
                        to_del.insert(0, i)
                for i in to_del:
                    del ev[i]
            return True
        except IndexError, e:
            print e
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
        except KeyError, e:
            print '%s: %s' % (e.__class__.__name__, e.message)
        for c in conf['chans']:
            serv.join(c)

    def on_pubmsg(self, serv, ev):
        helper = {'message': ev.arguments()[0],
                  'sender': ev.source().split('!')[0],
                  'chan': self.channels[ev.target()],
                  'target': ev.target()
                 }
        try:
            if 'pubmsg' in self.events:
                assert isinstance(self.events['pubmsg'], list)
                answered = False
                for plugin_event in self.events['pubmsg']:
                    #print '[%s] Calling plugin %s' %\
                    #(datetime.datetime.now().strftime('%H:%M:%S'),
                    #        plugin_event['plugin']),
                    if 'command_prefix' in conf and helper['message'].startswith(conf['command_prefix']):
                        if 'command_namespace' in plugin_event:
                            command_call = conf['command_prefix']+plugin_event['command_namespace']
                            if helper['message'].lower().startswith(command_call+' ') or helper['message'].lower() == command_call:
                                # on appelle une commande
                                cmd_len = len(conf['command_prefix']+plugin_event['command_namespace']+' ')
                                message = helper['message']
                                helper['message'] = helper['message'][cmd_len:]
                                args = helper['message'].split(' ')
                                command = args.pop(0)
                                answered = self.registered_plugins[plugin_event['plugin']].on_cmd(serv, ev, command, args, helper)
                                #print '%s' % answered
                                helper['message'] = message
                    else:
                        if not plugin_event['exclusive'] or not answered:
                            try:
                                answered = answered or self.registered_plugins[plugin_event['plugin']].on_pubmsg(serv, ev, helper)
                                #print '%s' % answered
                            except KeyError, e: # si on désactive le plugin, ça n’arrête pas la boucle
                                print '%s: %s' % (e.__class__.__name__, e.message)
        except Exception, e:
            print '%s: %s' % (e.__class__.__name__, e.message)

    def on_privmsg(self, serv, ev):
        helper = {'message': ev.arguments()[0],
                  'sender': ev.source().split('!')[0],
                  'target': ev.source().split('!')[0]
                 }
        try:
            if 'privmsg' in self.events:
                assert isinstance(self.events['privmsg'], list)
                answered = False
                for plugin_event in self.events['privmsg']:
                    if 'command_prefix' in conf and helper['message'].startswith(conf['command_prefix']):
                        if 'command_namespace' in plugin_event:
                            command_call = conf['command_prefix']+plugin_event['command_namespace']
                            if helper['message'].lower().startswith(command_call+' ') or helper['message'].lower() == command_call:
                                # on appelle une commande
                                cmd_len = len(conf['command_prefix']+plugin_event['command_namespace']+' ')
                                helper['message'] = helper['message'][cmd_len:]
                                args = helper['message'].split(' ')
                                command = args.pop(0)
                                answered = self.registered_plugins[plugin_event['plugin']].on_cmd(serv, ev, command, args, helper)
                    else:
                        if not plugin_event['exclusive'] or not answered:
                            try:
                                answered = answered or self.registered_plugins[plugin_event['plugin']].on_privmsg(serv, ev, helper)
                            except KeyError, e: # si on désactive le plugin, ça n’arrête pas la boucle
                                print '%s: %s' % (e.__class__.__name__, e.message)
        except Exception, e:
            print '%s: %s' % (e.__class__.__name__, e.message)

    def on_action(self, serv, ev):
        helper = {'message': ev.arguments()[0],
                  'sender': ev.source().split('!')[0],
                  #'chan': self.channels[ev.target()],
                  'target': ev.target()
                 }
        if ev.target() in self.channels:
            helper['chan'] = self.channels[ev.target()]
        try:
            if 'action' in self.events:
                assert isinstance(self.events['action'], list)
                answered = False
                for plugin_event in self.events['action']:
                    if not plugin_event['exclusive'] or not answered:
                        answered = answered or self.registered_plugins[plugin_event['plugin']].on_action(serv, ev, helper)
        except Exception, e:
            print '%s: %s' % (e.__class__.__name__, e.message)

    def on_join(self, serv, ev):
        helper = {'chan': self.channels[ev.target()],
                  'sender': ev.source().split('!')[0],
                  'target': ev.target()
                 }
        try:
            if 'join' in self.events:
                assert isinstance(self.events['join'], list)
                answered = False
                for plugin_event in self.events['join']:
                    if not plugin_event['exclusive'] or not answered:
                        answered = answered or self.registered_plugins[plugin_event['plugin']].on_join(serv, ev, helper)
        except Exception, e:
            print '%s: %s' % (e.__class__.__name__, e.message)

    def on_kick(self, serv, ev):
        helper = {'victim': ev.arguments()[0],
                  'message': ev.arguments()[1],
                  'sender': ev.source().split('!')[0],
                  'chan': self.channels[ev.target()],
                  'target': ev.target(),
                 }
        try:
            if 'kick' in self.events:
                assert isinstance(self.events['kick'], list)
                answered = False
                for plugin_event in self.events['kick']:
                    if not plugin_event['exclusive'] or not answered:
                        answered = answered or self.registered_plugins[plugin_event['plugin']].on_kick(serv, ev, helper)
        except Exception, e:
            print '%s: %s' % (e.__class__.__name__, e.message)

    def on_run(self, serv, ev):
        for chan_name, chan in self.channels.items():
            helper = {'chan': chan,
                      'target': chan_name
                     }
            try:
                if 'run' in self.events:
                    assert isinstance(self.events['run'], list)
                    for plugin_event in self.events['run']:
                        if datetime.datetime.now() >= self.runs[chan_name][plugin_event['plugin']]:
                            if isinstance(plugin_event['frequency'], tuple):
                                self.runs[chan_name][plugin_event['plugin']] += \
                                    datetime.timedelta(0, random.randint(*plugin_event['frequency']))
                            else:
                                self.runs[chan_name][plugin_event['plugin']] += \
                                    datetime.timedelta(0, plugin_event['frequency'])
                            self.registered_plugins[plugin_event['plugin']].on_run(serv, helper)

            except Exception, e:
                print '%s: %s' % (e.__class__.__name__, e.message)

    def get_config(self, plugin, name, default=None):
        try:
            path = os.path.join(os.path.dirname(sys.argv[0]), 'data', self.config_name, plugin.__class__.__name__)
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
            path = os.path.join(os.path.dirname(sys.argv[0]), 'data', self.config_name, plugin.__class__.__name__)
            try:
                os.makedirs(path)
            except OSError:
                pass
            with open(os.path.join(path, name), 'wb') as data_file:
                pickle.dump(data, data_file)
                return True
        except (OSError, IOError):
            return False

    def bold(self, text):
        return '%s%s%s' % (self.bold_char, text, self.bold_char)

    def color(self, text, color, background=None):
        if background:
            color_str = self.color_char % (self.background_color_char %
                                           (self.colors[color],
                                            self.colors[background]))
        else:
            color_str = self.color_char % self.colors[color]
        return '%s%s%s' % (color_str, text, self.reset_char)

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

    Nicebot(conf, plugins_conf, results.config_file).start()
