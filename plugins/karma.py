# -*- coding: utf-8 -*-

import re
import random

from stdPlugin import stdPlugin

# Universal quantifier on a sequence.
def forall(sequence, predicate):
    return reduce(lambda x, y: x and y, map(predicate, sequence), True)

# Existential quantifier on a sequence.
def exists(list, property):
    return reduce(lambda x, y: x or y, map(predicate, sequence), False)

class karma(stdPlugin):
    u'''Chaque terme suivi de '++' ou '--' se voit attribuer un karma en conséquence. Par exemple, « fromage++ ».'''

    events = {'pubmsg': {'exclusive': False, 'command_namespace': 'karma'},
              'privmsg': {'exclusive': False, 'command_namespace': 'karma'},
              'action': {'exclusive': False},
             }

    # A bit complicated, since we allow "-" but not "--" inside a word.
    regexp_pos = re.compile(r"(([\w\_'/]-?)+)\+\+", re.U)
    regexp_neg = re.compile(r"(([\w\_'/]-?)+)--", re.U)

    # Discard small words
    min_word_size = 3

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

    def react_karma_pos(self, k):
        """Returns an appropriate sentence for the given (positive) karma."""
        # If we were using python3, we could do stuff like "42 in
        # range(10, 1000000000)", which runs in O(1). But not with
        # python2 :(
        if k <= 2:
            return u"Intéressant, %s."
        if k <= 4:
            return u"C'est cool %s !"
        if k <= 8:
            return u"Yeah, j'adore %s \o/"
        if k <= 16:
            return u"/me trouve que %s est absolument génial ♥"
        if k <= 32:
            return u"Waou, je n'ai jamais vu quelque chose d'aussi monstrueusement génial que %s !"
        if k <= 64:
            return u"/me se pâme d'admiration devant %s"
        if k <= 128:
            return u"Que dire de plus quand on a %s ?"
        return u"/me se suicide de bonheur à cause de %s"

    def react_karma_neg(self, k):
        """Same function for negative karma."""
        k = abs(k)
        if k <= 2:
            return u"Pas génial, %s."
        if k <= 4:
            return u"Mouais, %s, c'est carrément bof."
        if k <= 8:
            return u"C'est nul, %s."
        if k <= 16:
            return u"Beuh, c'est carrément naze, %s :("
        if k <= 32:
            return u"Qui a eu l'idée d'inventer %s ? C'est vraiment un abruti."
        if k <= 64:
            return u"/me vomit sur %s"
        if k <= 128:
            return u"Chuck Norris a cherché pire que %s. Il est revenu en pleurant."
        return u"/me préfère se suicider plutôt que de parler de %s"

    def find_all_karma(self, message, plus):
        """Returns the list of words that were used """
        if plus:
            r = self.regexp_pos
        else:
            r = self.regexp_neg
        # In the regexp, we must use a second pair of parentheses to
        # group things, which causes re.findall() to output a list of
        # couples. Quick fix.
        return [x[0] for x in r.findall(message) if len(x[0]) >= self.min_word_size]

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
        """Try to match a word known in the karma database, and react
        accordingly.  To (somewhat) avoid spam, we only react to one
        word in the message, the one with the greatest absolute
        karma."""
        words = [w.strip(self.punctuation) for w in message.split()]
        candidates = [(w, self.get_karma(chan, w)) for w in words]
        if not words or forall(candidates, lambda (w, k) : k == 0):
            return False
        # Sort by decreasing absolute karma
        candidates.sort(key=(lambda (word, karma) : -abs(karma)))
        # Select all words with the greatest absolute karma
        (_, karma) = candidates[0]
        chosen_words = [(w, k) for (w, k) in candidates if abs(k) == abs(karma)]
        random.shuffle(chosen_words)
        (chosen_word, karma) = chosen_words[0]
        if karma > 0:
            answer = self.react_karma_pos(karma) % chosen_word
        if karma < 0:
            answer = self.react_karma_neg(karma) % chosen_word
        if answer.startswith(u"/me "):
            serv.action(chan, answer[4:])
        else:
            serv.privmsg(chan, answer)
        return True

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
        self.karma[chan] = self.bot.get_config(self, chan, dict())

    def save_karmadb(self, chan):
        return self.bot.write_config(self, chan, self.karma[chan])
