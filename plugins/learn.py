# -*- coding: utf-8 -*-

from stdPlugin import stdPlugin
from lib.markov import Markov

class learn(stdPlugin):
    u'''Apprend continuellement les mots utilisés sur un canal, et génère des phrases aléatoires et stupides.'''

    events = {'pubmsg': {'exclusive': False, 'command_namespace': 'say'},
              'privmsg': {'exclusive': False, 'command_namespace': 'say'},
              'action': {'exclusive': False},
              'join': {'exclusive': False},
              'run': {'frequency': (300, 30000)},
             }
    markov = Markov()

    def __init__(self, bot, conf):
        return_val = super(learn, self).__init__(bot, conf)
        chans = self.bot.conf['chans'] if not self.bot.channels else self.bot.channels
        for chan in chans:
            self.get_dico(chan)
        return return_val

    def parse(self, chan, message):
        self.markov.add_sentence(chan, message)
        self.save_dico(chan)

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
                serv.privmsg(helper['target'], self.markov.get_sentence(helper['target']))
                return True
            else:
                serv.privmsg(helper['target'], self.markov.get_sentence(helper['target'], args[0]))
                return True
        #elif command == 'save':
        #    if self.save_dico(helper['target']):
        #        serv.privmsg(helper['target'], u'Dictionnaire sauvegardé : %d mots' % self.get_stats(helper['target']))
        #        return True
        #    else:
        #        serv.privmsg(helper['target'], u'Erreur lors de la sauvegarde du dictionnaire !')
        #        return True
        elif command == 'stats':
            serv.privmsg(helper['target'], u'Mot connus : %d' % self.markov.get_stats(helper['target']))
            return True
        else:
            serv.privmsg(helper['target'], u'Je ne connais pas cette commande.')
            return True

    def get_dico(self, chan):
        data = self.bot.get_config(self, chan, self.markov.default_data())
        self.markov.load(chan, data)

    def save_dico(self, chan):
        data = self.markov.dump(chan)
        return self.bot.write_config(self, chan, data)

    def on_run(self, serv, helper):
        serv.privmsg(helper['target'], self.markov.get_sentence(helper['target']))
