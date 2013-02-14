# -*- coding: utf-8 -*-

import datetime
import twitter
from stdPlugin import stdPlugin, PluginError

class microblogging(stdPlugin):
    u'''Permet d’interagir avec un compte de microblogging (statusnet/twitter)'''

    events = {'pubmsg': {'exclusive': True, 'command_namespace': 'truite'},
              'run': {'frequency': 300}}

    status_length = 140

    def __init__(self, bot, conf):
        return_val = super(microblogging, self).__init__(bot, conf)
        self.api = twitter.Twitter(auth=twitter.OAuth(**conf))
        if not self.api.account.verify_credentials():
            raise PluginError('Invalid microblogging credentials!')
        self.last_fetch = self.bot.get_config(self, 'last_fetch', None)

    def send_status(self, message):
        self.api.statuses.update(status=message)
        return True

    def on_cmd(self, serv, ev, command, args, helper):
        u'''%(namespace)s <message> : Publie un message de microblogging
        '''
        if not command:
            return False
        else:
            args.insert(0, command)
            message = ' '.join(args)
            if len(message) > self.status_length:
                serv.privmsg(helper['target'], u'Trop gros, passera '\
                            +u'pas (%d caractères)' % len(message))
                return True
            try:
                self.send_status(message)
                serv.privmsg(helper['target'], u'C’est envoyé !')
                return True
            except Exception, e:
                serv.privmsg(helper['target'], u'Erreur lors de '\
                                               +u'l’envoi : %s' % e)
        return False

    def on_run(self, serv, helper):
        params = {}
        if self.last_fetch:
            params['since_id'] = self.last_fetch
        mentions = self.api.statuses.mentions_timeline(**params)
        for mention in mentions:
            serv.privmsg(helper['target'], u'@%s : %s' % \
                    (mention['user']['screen_name'], mention['text']))
        self.bot.write_config(self, 'last_fetch', mentions[-1]['id'])
