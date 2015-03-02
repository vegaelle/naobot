# -*- coding: utf-8 -*-

import random
import re
from stdPlugin import stdPlugin


class discuss(stdPlugin):
    u'''Tente d’engager la conversation sur un canal.'''

    events = {'pubmsg': {'exclusive': True},
              'privmsg': {'exclusive': True},
              'action': {'exclusive': True},
              'join': {'exclusive': True},
              'kick': {'exclusive': True},
              }

    def random_sentence(self, serv, ev, helper, type, vars):
        try:
            sentence = random.choice(self.sentences[type])
            if hasattr(sentence, '__call__'):
                result = sentence(serv, ev, helper)
                return result
            else:
                self.say(serv, helper['target'], sentence % vars)
                return True
        except KeyError:
            return False

    def on_pubmsg(self, serv, ev, helper):
        if helper['message'].lower().find(serv.username.lower()) >= 0:
            vars = {'nick': helper['sender'],
                    'message': helper['message'],
                    'chan': helper['target'],
                    }
            if helper['message'].lower().find('ping') >= 0:
                self.say(serv, helper['target'], u'%(nick)s: pong' % vars)
                return True
            if helper['message'].lower().find('yin') >= 0:
                self.say(serv, helper['target'], u'%(nick)s: yang' % vars)
                return True
            else:
                return self.random_sentence(serv, ev, helper, 'mention', vars)
        else:
            return False

    def on_action(self, serv, ev, helper):
        return self.on_pubmsg(serv, ev, helper)

    def on_join(self, serv, ev, helper):
        if helper['sender'] == serv.username:  # si c’est notre propre join
            vars = {'chan': helper['target'],
                    }
            return self.random_sentence(serv, ev, helper, 'joining', vars)
        else:
            return False

    def on_kick(self, serv, ev, helper):
        vars = {'nick': helper['sender'],
                'message': helper['message'],
                'chan': helper['target'],
                'victim': helper['victim'],
                }
        return self.random_sentence(serv, ev, helper, 'kick', vars)

    def answer_message(self, serv, ev, helper):
        message = re.sub(serv.username, helper['sender'], helper['message'])
        if ev.eventtype() == 'pubmsg' or ev.eventtype() == 'privmsg':
            serv.privmsg(helper['target'], message)
        elif ev.eventtype() == 'action':
            serv.action(helper['target'], message)
        else:
            print ev.eventtype()
        return True

    def on_cmd(self, serv, ev, command, args, helper):
        serv.privmsg(helper['target'], 'Je ne connais pas la commande %s' %
                     command)
        return True

    def __init__(self, bot, conf):
        # déclaration des différentes phrases
        self.sentences = {'mention': [u'/me mange %(nick)s',
                                      u'Hein ?',
                                      self.answer_message,
                                      u'Ho, ta gueule %(nick)s',
                                      ],
                          'joining': [u'Coucou, tu veux voir mon bit ?',
                                      u'Ohai %(chan)s o/',
                                      u'Faites comme si j’étais pas là.',
                                      u'De toutes façons, il meurt à la fin.',
                                      u'’Matin !',
                                      ],
                          'kick': [u'Bon débarras.',
                                   u'J’en avais marre de %(victim)s de toutes '
                                   u'façons',
                                   u'Haha.',
                                   ],
                          }
        return super(discuss, self).__init__(bot, conf)
