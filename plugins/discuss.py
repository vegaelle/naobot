# -*- coding: utf-8 -*-

import random
from datetime import datetime
import re
from stdPlugin import stdPlugin

class discuss(stdPlugin):

    events = [('pubmsg', {'priority': 1, 'exclusive': True, 'command_namespace': 'say'})]

    def on_pubmsg(self, serv, ev, helper):
        if helper['message'].find(serv.username) >= 0:
            sentence = random.choice(self.sentences['mention'])
            if hasattr(sentence, '__call__'):
                result = sentence(serv, ev, helper)
                return result
            else:
                vars = {'nick': helper['sender'],
                        'message': helper['message'],
                        'chan': ev.target(),
                        }
                self.say(serv, ev.target(), self.template(sentence, vars))
                return True

    def answer_message(self, serv, ev, helper):
        message = re.sub(serv.username, helper['sender'], helper['message'])
        if ev.eventtype() == 'pubmsg' or ev.eventtype() == 'privmsg':
            serv.privmsg(ev.target(), message)
        elif ev.eventtype() == 'action':
            self.action(ev.target(), message)
        else:
            print ev.eventtype()
        return True

    def on_cmd(self, serv, ev, command, args):
        serv.privmsg(ev.target(), 'Je ne connais pas la commande %s' % command)
        return True

    def __init__(self, bot):
        # déclaration des différentes phrases
        self.sentences = {'mention': [u'/me mange {{ nick }}',
                                 u'Hein ?',
                                 self.answer_message,
                                 ]}
        return super(discuss, self).__init__(bot)
