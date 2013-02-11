# -*- coding: utf-8 -*-

import twitter
from stdPlugin import stdPlugin, PluginError

class microblogging(stdPlugin):
    u'''Permet d’interagir avec un compte de microblogging (statusnet/twitter)'''

    events = {'pubmsg': {'exclusive': True, 'command_namespace': 'tweet'}}

    def __init__(self, bot, conf):
        return_val = super(quote, self).__init__(bot, conf)
        self.api = twitter.Twitter(auth=twitter.Oauth(**conf))
        if not self.api.account.verify_credentials():
            raise PluginError('Invalid microblogging credentials!')
        return return_val

    def on_cmd(self, serv, ev, command, args, helper):
        u'''%(namespace)s <phrase> : enregistre une phrase ridicule prononcée
        par un membre du chan.
        %(namespace)s : sélectionne une phrase de la liste.
        %(namespace)s #<id> : sélectionne la phrase d’un id donné.
        %(namespace)s ?<mot-clé> : sélectionne une phrase contenant le mot-clé'''
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
        else:
            args.insert(0, command)
            quote = ' '.join(args)
            id = self.add_quote(helper['target'], quote, helper['sender'])
            if id:
                serv.privmsg(helper['target'], u'Quote enregistrée ! ID %d' % id)
                return True
        return False
