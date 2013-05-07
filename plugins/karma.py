# -*- coding: utf-8 -*-

import re

from stdPlugin import stdPlugin

class karma(stdPlugin):
    u'''Chaque terme suivi de '++' ou '--' se voit attribuer un karma en conséquence. Par exemple, « fromage++ ».'''

    events = {'pubmsg': {'exclusive': False, 'command_namespace': 'karma'},
              'privmsg': {'exclusive': False, 'command_namespace': 'karma'},
              'action': {'exclusive': False},
             }

    regexp_pos = re.compile(r"([\w\-_/]+)\+\+", re.U)
    regexp_neg = re.compile(r"([\w\-_/]+)--", re.U)
    
    # chan -> (word -> karma)
    # karma is an integer
    karma = dict()

    def __init__(self, bot, conf):
        return_val = super(karma, self).__init__(bot, conf)
        chans = self.bot.conf['chans'] if not self.bot.channels else self.bot.channels
        for chan in chans:
            self.load_karmadb(chan)
        return return_val

    def get_karma(self, chan, word):
        word = word.lower()
        if word in self.karma[chan]:
            return self.karma[chan][word]
        else:
            return 0

    def modify_karma(self, chan, word, incr):
        # rstrip to get rid of the additional "-" at the end
        # (could we find a better regexp?)
        word = word.lower().rstrip('-')
        if word in self.karma[chan]:
            self.karma[chan][word] += incr
        else:
            self.karma[chan][word] = incr

    def increase_karma(self, chan, word):
        self.modify_karma(chan, word, 1)

    def decrease_karma(self, chan, word):
        self.modify_karma(chan, word, -1)


    def parse(self, chan, message):
        changed = False
        for word in self.regexp_pos.findall(message):
            self.increase_karma(chan, word)
            changed = True
        for word in self.regexp_neg.findall(message):
            self.decrease_karma(chan, word)
            changed = True
        if changed:
            self.save_karmadb(chan)

    def on_pubmsg(self, serv, ev, helper):
        self.parse(helper['target'], helper['message'])
        return False

    def on_privmsg(self, serv, ev, helper):
        self.parse(helper['target'], helper['message'])
        return False

    def on_action(self, serv, ev, helper):
        self.parse(helper['target'], helper['message'])
        return False

    def on_join(self, serv, ev, helper):
        if helper['sender'] == serv.username: #s’il s’agit de notre propre join
            self.load_karmadb(helper['target'])
            return False
        else:
            return False

    def on_cmd(self, serv, ev, command, args, helper):
        u'''%(namespace)s <word> : display the karma of <word>.'''
        chan = helper['target']
        if command:
            k = self.get_karma(chan, command)
            serv.privmsg(chan, u'Karma for « %s » : %d.' % (command, k))
        else:
            serv.privmsg(chan, u'Need a word.')

    def load_karmadb(self, chan):
        self.karma[chan] = dict()
        # TODO: Save and load from disk

    def save_karmadb(self, chan):
        pass
