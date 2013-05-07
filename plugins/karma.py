# -*- coding: utf-8 -*-

import re

from stdPlugin import stdPlugin

class karma(stdPlugin):
    u'''Chaque terme suivi de '++' ou '--' se voit attribuer un karma en conséquence. Par exemple, « fromage++ ».'''

    events = {'pubmsg': {'exclusive': False, 'command_namespace': 'karma'},
              'privmsg': {'exclusive': False, 'command_namespace': 'karma'},
              'action': {'exclusive': False},
             }

    # A bit complicated, since we allow "-" but not "--" inside a word.
    regexp_pos = re.compile(r"(([\w\_'/]-?)+)\+\+", re.U)
    regexp_neg = re.compile(r"(([\w\_'/]-?)+)--", re.U)

    punctuation = u",.  !?"
    
    # chan -> (word -> karma)
    # karma is an integer
    karma = dict()

    def __init__(self, bot, conf):
        return_val = super(karma, self).__init__(bot, conf)
        chans = self.bot.conf['chans'] if not self.bot.channels else self.bot.channels
        for chan in chans:
            self.load_karmadb(chan)
        return return_val

    def find_all_karma(self, message, plus):
        """Returns the list of words that were used """
        if plus:
            r = self.regexp_pos
        else:
            r = self.regexp_neg
        # In the regexp, we must use a second pair of parentheses to
        # group things, which causes re.findall() to output a list of
        # couples. Quick fix.
        return [x[0] for x in r.findall(message)]

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


    def parse_karma(self, chan, message):
        changed = False
        for word in self.find_all_karma(message, plus=True):
            self.increase_karma(chan, word)
            changed = True
        for word in self.find_all_karma(message, plus=False):
            self.decrease_karma(chan, word)
            changed = True
        if changed:
            self.save_karmadb(chan)

    def match_words(self, serv, chan, message):
        """Try to match a word known in the karma database, and react accordingly."""
        answered = False
        words = [w.strip(self.punctuation) for w in message.split()]
        for w in words:
            k = self.get_karma(chan, w)
            if k > 0:
                serv.privmsg(chan, u"Yeah, j'adore %s \o/" % w)
                answered = True
            if k < 0:
                serv.privmsg(chan, u"C'est nul, %s" % w)
                answered = True
        return answered

    def on_pubmsg(self, serv, ev, helper):
        self.parse_karma(helper['target'], helper['message'])
        return self.match_words(serv, helper['target'], helper['message'])

    def on_privmsg(self, serv, ev, helper):
        self.parse_karma(helper['target'], helper['message'])
        return self.match_words(serv, helper['target'], helper['message'])

    def on_action(self, serv, ev, helper):
        self.parse_karma(helper['target'], helper['message'])
        return self.match_words(serv, helper['target'], helper['message'])

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
