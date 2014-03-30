# -*- coding: utf-8 -*-

import subprocess
import re
from stdPlugin import stdPlugin


class ping(stdPlugin):
    u'''Permet de vérifier si plusieurs machines répondent au ping'''

    events = {'pubmsg': {'exclusive': True, 'command_namespace': 'ping'}}

    def __init__(self, bot, conf):
        return_val = super(ping, self).__init__(bot, conf)
        self.machines = conf['machines']
        self.regex = re.compile('([0-9]{1,3})% packet loss')
        return return_val

    def ping(self, machine):
        ping = subprocess.Popen(['ping', '-c', '4', machine],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, error = ping.communicate()
        match = self.regex.search(out)
        if not match:
            return None
        else:
            loss = match.group(1)
            return int(loss)

    def on_cmd(self, serv, ev, command, args, helper):
        u'''%(namespace)s : Vérifie le ping sur toutes les machines.'''
        try:
            pings = 0
            for machine in self.machines:
                ping = self.ping(machine)
                if ping == 0:
                    pings += 1
                elif ping is None or ping == 100:
                    serv.privmsg(helper['target'], u'%s ne répond pas !' %
                                 machine)
                else:
                    serv.privmsg(helper['target'], u'%s répond avec %d%% de'
                                 + 'pertes' % (machine, ping))
                    pings += 1
            serv.privmsg(helper['target'], u'%d machine%s sur %d répond%s' %
                         (pings, ('s' if pings > 1 else ''),
                          len(self.machines), ('ent' if pings > 1 else '')))
        except Exception, e:
            serv.privmsg(helper['target'], u'Fail : %s.' % e.message)
        return False
