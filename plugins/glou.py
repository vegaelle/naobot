# -*- coding: utf-8 -*-

from stdPlugin import stdPlugin

class glou(stdPlugin):
    u'''Étanche la soif des utilisateurs.'''

    events = {'pubmsg': {'exclusive': True, 'command_namespace': 'glou'}}

    def on_cmd(self, serv, ev, command, args, helper):
        u'''%(namespace)s : sert une bière à celui qui la demande
        %(namespace)s <nom> : sert une bière à <nom>'''
        if not command:
            serv.action(helper['target'], u'sert une bière bien fraîche à %s.' %
                                          helper['sender'])
        else:
            serv.action(helper['target'], u'sert une bière bien fraîche à %s.' %
                                          command)
        return True
