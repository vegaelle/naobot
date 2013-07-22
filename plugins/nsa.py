# -*- coding: utf-8 -*-

import random
import os
from stdPlugin import stdPlugin, PluginError

class nsa(stdPlugin):
    u'''Attire l’attention de la National Security Agency sur le chan.'''

    events = {
            'run': {'frequency': (1200, 12000)},
        }

    def __init__(self, bot, conf):
        return_val = super(nsa, self).__init__(bot, conf)
        try:
            file = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'nsa')).read()
            self.words = file.replace('\n', ' ').split(', ')
        except Exception, e:
            raise PluginError('No words found: %s.' % e)
        return return_val

    def gen_sentence(self):
        sentence = []
        for i in xrange(random.randint(5, 15)):
            sentence.append(random.choice(self.words))
        return ' '.join(sentence)

    def on_run(self, serv, helper):
        serv.privmsg(helper['target'], self.gen_sentence())



