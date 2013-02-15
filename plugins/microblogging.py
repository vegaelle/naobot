# -*- coding: utf-8 -*-

import datetime
import HTMLParser
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

    def send_status(self, message, reply=None):
        params = {'status': message}
        if reply:
            params['in_reply_to_status_id'] = reply
        result = self.api.statuses.update(**params)
        return result['id']

    def repeat_status(self, id):
        result = self.api.statuses.retweet(id=id)
        return result['id']

    def del_status(self, id):
        result = self.api.statuses.destroy(id=id)
        return result['id']

    def on_cmd(self, serv, ev, command, args, helper):
        u'''%(namespace)s <message> : Publie un message de microblogging
        %(namespace)s ?<ID> <message> : Publie un message en réponse à un message donné
        %(namespace)s +<ID> : Répète le message donné
        %(namespace)s !<ID> : Supprime le message donné (réservé aux admins)
        '''
        if not command:
            return False
        elif command.startswith('?'):
            message = ' '.join(args)
            try:
                id = self.send_status(message, command[1:])
                serv.privmsg(helper['target'], u'c’est envoyé (%d) !' % id)
                return True
            except exception, e:
                serv.privmsg(helper['target'], u'erreur lors de '\
                                               +u'l’envoi : %s' % e.message)
            except:
                serv.privmsg(helper['target'], u'Fail.')
        elif command.startswith('+'):
            try:
                self.repeat_status(command[1:])
                serv.privmsg(helper['target'], u'Message répété.')
            except:
                serv.privmsg(helper['target'], u'Fail.')
        elif command.startswith('!'):
            if 'admin' in self.bot.registered_plugins:
                try:
                    if self.bot.registered_plugins['admin'].is_admin(ev.source()):
                        self.del_status(command[1:])
                        serv.privmsg(helper['target'], u'Message supprimé.')
                    else:
                        serv.privmsg(helper['target'], u'Nope.')
                except:
                    serv.privmsg(helper['target'], u'Fail.')
        else:
            args.insert(0, command)
            message = ' '.join(args)
            try:
                id = self.send_status(message)
                serv.privmsg(helper['target'], u'c’est envoyé (%d) !' % id)
                return True
            except exception, e:
                serv.privmsg(helper['target'], u'erreur lors de '\
                                               +u'l’envoi : %s' % e.message)
        return False

    def on_run(self, serv, helper):
        params = {}
        if self.last_fetch:
            params['since_id'] = self.last_fetch
        mentions = self.api.statuses.mentions_timeline(**params)
        self.last_fetch = mentions[0]['id']
        mentions.reverse()
        h = HTMLParser.HTMLParser()
        for mention in mentions:
            serv.privmsg(helper['target'], u'@%s : %s (%d)' % \
                    (mention['user']['screen_name'], h.unescape(mention['text']), mention['id']))
        self.bot.write_config(self, 'last_fetch', self.last_fetch)
