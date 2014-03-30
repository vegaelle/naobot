# -*- coding: utf-8 -*-

import random
from stdPlugin import stdPlugin


class glou(stdPlugin):
    u'''Étanche la soif des utilisateurs.'''

    events = {'pubmsg': {'exclusive': True, 'command_namespace': 'glou'}}

    def on_cmd(self, serv, ev, command, args, helper):
        u'''%(namespace)s : sert une bière à celui qui la demande
        %(namespace)s <nom> : sert une bière à <nom>'''
        if not command:
            if random.randint(0, 20) < 1:
                serv.action(helper['target'], u'lance un dindon sur %s.' %
                                              helper['sender'])
            else:
                serv.action(helper['target'], u'sert une bière bien fraîche à'
                            u' %s.' % helper['sender'])
        else:
            args.insert(0, command)
            name = (' '.join(args))
            if random.randint(0, 20) < 1:
                serv.action(helper['target'], u'lance un dindon sur %s.' %
                                              name)
            else:
                serv.action(helper['target'], u'sert une bière bien fraîche à'
                            u' %s.' % name)
        return True
