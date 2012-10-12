# -*- coding: utf-8 -*-

import re
import random
from stdPlugin import stdPlugin

class learn(stdPlugin):

    events = {'pubmsg': {'priority': 1, 'exclusive': False, 'command_namespace': 'say'},
              'privmsg': {'priority': 1, 'exclusive': False, 'command_namespace': 'say'},
              'action': {'priority': 1, 'exclusive': False},

              'join': {'priority': 1, 'exclusive': False},
             }

    dico = {}
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
        self.dico[chan] = self.bot.get_config(self, chan, {})

    def save_dico(self, chan):
        return self.bot.write_config(self, chan, self.dico[chan])

    def parse(self, chan, sentence):
        sentences = re.split(self.end_chars, sentence)
        for sentence in sentences:
            current_word = 0
            words = sentence.split()
            last_word = len(words) - 1
            for word in words:
                if current_word == 0:
                    self.add_successor_to_word(chan, self.begin_word, word)
                else:
                    self.add_successor_to_word(chan, words[current_word-1], word)
                if current_word == last_word:
                    self.add_successor_to_word(chan, word, self.end_word)
                current_word += 1
        self.save_dico(chan)

    def get_sentence(self, chan, begin=None):
        if begin is None:
            begin = self.begin_word
            current_word = self.get_random_next_word(chan, begin)
        elif begin not in self.dico[chan]:
            return 'Je ne connais pas ce mot.'
        else:
            current_word = begin
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

    def add_successor_to_word(self, chan, word, successor):
        if word not in self.dico[chan]:
            self.dico[chan][word] = {}
        if successor in self.dico[chan][word]:
            self.dico[chan][word][successor] += 1
        else:
            self.dico[chan][word][successor] = 1

    def get_random_next_word(self, chan, word):
        word_list = []
        for key, weight in self.dico[chan][word].items():
            for i in range(0, weight):
                word_list.append(key)
        result = random.choice(word_list)
        return result
