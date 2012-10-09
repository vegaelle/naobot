# -*- coding: utf-8 -*-

import re

class stdPlugin(object):
    def on_pubmsg(self, serv, ev, helper):
        return False
    
    def on_event(self, serv, ev, helper):
        return False

    def say(self, serv, target, message):
        if message.startswith('/me'):
            serv.action(target, message[3:])
        else:
            serv.privmsg(target, message)

    def template(self, message, values):
        try:
            assert isinstance(values, dict)
            for i in values.iterkeys():
                message = re.sub('{{ %s }}' % i, values[i], message)
            return message
        except AssertionError:
            return message
