# -*- coding: utf-8 -*-

from irc import bot

conf = {'server': [('irc.geeknode.org', 6667)],
        'nick': 'Nicebot',
        'fullname': 'Le bot IRC du Nicelab'}

class Nicebot(bot.SingleServerIRCBot):

    def __init__(self):
        bot.SingleServerIRCBot.__init__(self, conf['server'], conf['nick'], conf['fullname'])
    def on_welcome(self, serv, ev):
        serv.join('#poney-gonflable')

    def on_pubmsg(self, serv, ev):
        message = ev.arguments()[0]
        sender = ev.source().split('!')[0]
        chan = self.channels[ev.target()]
        if message.find(serv.username) >= 0:
            serv.privmsg(ev.target(), u'Qui vous autorise, %s ?' % sender)

if __name__ == '__main__':
    Nicebot().start()
