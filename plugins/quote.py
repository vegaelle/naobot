# -*- coding: utf-8 -*-

import datetime
import random
from stdPlugin import stdPlugin


class quote(stdPlugin):
    u'''Permet d’enregistrer et de répéter des phrases embarassantes..'''

    events = {'pubmsg': {'exclusive': True, 'command_namespace': 'quote'}}

    def __init__(self, bot, conf):
        return_val = super(quote, self).__init__(bot, conf)
        self.dico = {}
        chans = self.bot.conf['chans'] if not self.bot.channels else\
            self.bot.channels
        for chan in chans:
            self.get_dico(chan)
        return return_val

    def get_dico(self, chan):
        data = self.bot.get_config(self, chan, [])
        self.dico[chan] = data

    def save_dico(self, chan):
        return self.bot.write_config(self, chan, self.dico[chan])

    def add_quote(self, chan, quote, author):
        if not len(self.dico[chan]):
            id = 1
        else:
            dico_index = dict((q['id'], i) for (i, q) in
                              enumerate(self.dico[chan]))
            id = max(dico_index) + 1
        self.dico[chan].append({'id': id,
                                'author': author,
                                'quote': quote,
                                'date': datetime.datetime.now()})
        self.save_dico(chan)
        return id

    def del_quote(self, chan, id):
        dico_index = dict((q['id'], i) for (i, q) in
                          enumerate(self.dico[chan]))
        quote_index = dico_index.get(int(id), -1)
        if quote_index == -1:
            return None
        else:
            del self.dico[chan][quote_index]
            self.save_dico(chan)

    def get_quote(self, chan, id):
        dico_index = dict((q['id'], i) for (i, q) in
                          enumerate(self.dico[chan]))
        quote_index = dico_index.get(int(id), -1)
        if quote_index == -1:
            return None
        else:
            return self.dico[chan][quote_index]

    def search_quote(self, chan, keyword):
        dico_index = dict((q['quote'], i) for (i, q) in
                          enumerate(self.dico[chan]))
        quotes_id = [i for q, i in dico_index.items() if keyword in q]
        quotes = []
        for i in quotes_id:
            quotes.append(self.dico[chan][i])
        return quotes

    def get_random_quote(self, chan):
        if not len(self.dico[chan]):
            return None
        return random.choice(self.dico[chan])

    def say_quote(self, serv, chan, quote):
        if quote:
            serv.privmsg(chan, '[#%d] %s' % (quote['id'], quote['quote']))
            return True
        else:
            serv.privmsg(chan, 'Quote introuvable')
            return False

    def on_cmd(self, serv, ev, command, args, helper):
        u'''%(namespace)s <phrase> : enregistre une phrase ridicule prononcée
            par un membre du chan.
        %(namespace)s : sélectionne une phrase de la liste.
        %(namespace)s #<id> : sélectionne la phrase d’un id donné.
        %(namespace)s ?<mot-clé> : sélectionne une phrase contenant le mot-clé
        %(namespace)s !<id> : supprime une phrase donnée (réservée aux
            admins)
        '''
        try:
            if not command:
                quote = self.get_random_quote(helper['target'])
                return self.say_quote(serv, helper['target'], quote)
            elif command.startswith('#'):
                quote = self.get_quote(helper['target'], command[1:])
                return self.say_quote(serv, helper['target'], quote)
            elif command.startswith('?'):
                args.insert(0, command)
                keyword = ' '.join(args)[1:]
                quotes = self.search_quote(helper['target'], keyword)
                if quotes:
                    quote = random.choice(quotes)
                    return self.say_quote(serv, helper['target'], quote)
                else:
                    return self.say_quote(serv, helper['target'], None)
            elif command.startswith('!'):
                if 'admin' in self.bot.registered_plugins:
                    if self.bot.registered_plugins['admin'].\
                            is_admin(ev.source()):
                        self.del_quote(helper['target'], command[1:])
                        serv.privmsg(helper['target'], u'Quote supprimée.')
                    else:
                        serv.privmsg(helper['target'], 'Leave my quote alone!')
            else:
                args.insert(0, command)
                quote = ' '.join(args)
                id = self.add_quote(helper['target'], quote, helper['sender'])
                if id:
                    serv.privmsg(helper['target'], u'Quote enregistrée ! ID %d'
                                 % id)
                    return True
        except Exception:
            serv.privmsg(helper['target'], u'Nope.')
        return False
