# -*- coding: utf-8 -*-

import re
import random
from stdPlugin import stdPlugin

class learn(stdPlugin):
    u'''Apprend continuellement les mots utilisés sur un canal, et génère des phrases aléatoires et stupides.'''

    events = {'pubmsg': {'priority': 1, 'exclusive': False, 'command_namespace': 'say'},
              'privmsg': {'priority': 1, 'exclusive': False, 'command_namespace': 'say'},
              'action': {'priority': 1, 'exclusive': False},

              'join': {'priority': 1, 'exclusive': False},
             }

    # We need to be able to build sentences forward *and* backward
    # from a given word.
    dico = {}
    backward_dico = {}
    begin_word = '|BEGIN|'
    end_word = '|END|'
    cut_chars = '[,;:]'
    end_chars = '[.!?]'
    blacklist = set()

    def __init__(self, bot, conf):
        return_val = super(learn, self).__init__(bot, conf)
        for chan in self.bot.channels:
            self.get_dico(chan)
        return return_val


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
            self.get_dico(helper['target'])
            return False
        else:
            return False

    def on_cmd(self, serv, ev, command, args, helper):
        u'''%(namespace)s sentence : génère une phrase aléatoire.
        %(namespace)s sentence <mot> : génère une phrase aléatoire contenant le mot donné, s’il est connu.
        %(namespace)s stats : indique le nombre de mots connus pour le canal courant'''
        if command == 'sentence':
            if len(args) == 0:
                serv.privmsg(helper['target'], self.get_sentence(helper['target']))
                return True
            else:
                serv.privmsg(helper['target'], self.get_sentence(helper['target'], args[0]))
                return True
        #elif command == 'save':
        #    if self.save_dico(helper['target']):
        #        serv.privmsg(helper['target'], u'Dictionnaire sauvegardé : %d mots' % self.get_stats(helper['target']))
        #        return True
        #    else:
        #        serv.privmsg(helper['target'], u'Erreur lors de la sauvegarde du dictionnaire !')
        #        return True
        elif command == 'stats':
            serv.privmsg(helper['target'], u'Mot connus : %d' % self.get_stats(helper['target']))
            return True
        else:
            serv.privmsg(helper['target'], u'Je ne connais pas cette commande.')
            return True

    def get_dico(self, chan):
        self.dico[chan], self.backward_dico[chan] = self.bot.get_config(self, chan, ({}, {}))

    def save_dico(self, chan):
        return self.bot.write_config(self, chan, (self.dico[chan], self.backward_dico[chan]))

    def parse(self, chan, sentence):
        # We don't want to keep empty sentences
        sentences = [s for s in re.split(self.end_chars, sentence) if s]
        for sentence in sentences:
            current_word = 1
            words = sentence.split()
            words.insert(0, self.begin_word)
            words.append(self.end_word)
            for word in words[1:]:
                self.add_relation(chan, self.dico, words[current_word-1], word)
                self.add_relation(chan, self.backward_dico, word, words[current_word-1])
                current_word += 1
        self.save_dico(chan)

    def get_key_nocase(self, word, dico):
        """Search for a key matching the given word (ignoring case).
        Returns the key found, or 'None' is none is found."""
        for k in dico:
            if k.lower() == word.lower():
                return k
        return None

    def get_sentence(self, chan, begin=None):
        if begin is None:
            begin = self.begin_word
            current_word = self.get_random_next_word(chan, begin)
        else:
            current_word = self.get_key_nocase(begin, self.dico[chan])
            if current_word is None:
                return 'Je ne connais pas ce mot.'
        sentence = current_word
        current_word = self.get_random_next_word(chan, current_word)
        while current_word != self.end_word:
            sentence += ' ' + current_word
            current_word = self.get_random_next_word(chan, current_word)
        return sentence

    def get_stats(self, chan):
        return len(self.dico[chan])

    def remove_word(self, chan, word):
        if word in self.dico[chan]:
            self.dico[chan].remove(word)

    def blacklist_word(self, word):
        self.blacklist.append(word)

    def un_blacklist_word(self, word):
        self.blacklist.remove(word)

    def get_blacklist(self):
        return self.blacklist

    def add_relation(self, chan, dico, word, related):
        if word not in dico[chan]:
            dico[chan][word] = {}
        if related in dico[chan][word]:
            dico[chan][word][related] += 1
        else:
            dico[chan][word][related] = 1

    def get_random_next_word(self, chan, word):
        word_list = []
        for key, weight in self.dico[chan][word].items():
            for i in range(0, weight):
                word_list.append(key)
        result = random.choice(word_list)
        return result
