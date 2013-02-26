# -*- coding: utf-8 -*-

import os
from stdPlugin import stdPlugin

class ping(stdPlugin):
    u'''Permet de vérifier si plusieurs machines répondent au ping'''

    events = {'pubmsg': {'exclusive': True, 'command_namespace': 'ping'}}

    def __init__(self, bot, conf):
        return_val = super(ping, self).__init__(bot, conf)
        self.machines = conf['machines']
        return return_val

    def ping(self, machine):
        return os.system('ping %s' % machine)

    def on_cmd(self, serv, ev, command, args, helper):
        u'''%(namespace)s : Vérifie le ping sur toutes les machines.'''
        try:
            pings = 0
            for machine in self.machines:
                if self.ping(machine):
                    pings += 1
                else:
                    serv.privmsg(helper['target'], u'%s ne répond pas !' % \
                                 machine)
            serv.privmsg(helper['target'], u'%d machine%s sur %d répond%s'%\
                         (pings, ('s' if pings > 1 else ''),
                          len(self.machines), ('ent' if pings > 1 else '')))
        except Exception, e:
            serv.privmsg(helper['target'], u'Fail : %s.' % e.message)
        return False

