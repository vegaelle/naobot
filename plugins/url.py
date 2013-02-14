# -*- coding: utf-8 -*-

import re
import urlparse
import requests
from BeautifulSoup import BeautifulSoup
from HTMLParser import HTMLParser
from stdPlugin import stdPlugin

class url(stdPlugin):
    u'''Récupère les URLs postées sur un chan et indique leur cible.'''

    events = {'pubmsg': {'exclusive': False},
              'privmsg': {'exclusive': False},
              'action': {'exclusive': False},
             }


    def on_pubmsg(self, serv, ev, helper):
        urls = re.findall("(?P<url>https?://[^\s]+)", helper['message'])
        answered = False
        if urls:
            for url in urls:
                try:
                    str_line = ''
                    req = requests.get(url, verify=False)
                    if req.url is not url and req.url+'/' is not url:
                        str_line += u'%s ' % req.url
                    content_type = req.headers['content-type'].split(';')[0].lower()
                    if content_type == 'text/html':
                        soup = BeautifulSoup(req.content)
                        title = soup.find('title')
                        if not title:
                            str_line += u'Page HTML sans titre'
                        else:
                            h = HTMLParser()
                            str_line += h.unescape(title.text.replace('\n', ' '))
                    else:
                        str_line += u'Document %s' % content_type
                    if str_line:
                        serv.privmsg(helper['target'], str_line)
                        answered = True
                except Exception as e:
                    serv.privmsg(helper['target'], u'Erreur de connexion à %s' % url)
        if answered:
            return True
        return False

    def on_privmsg(self, serv, ev, helper):
        return self.on_pubmsg(serv, ev, helper)

    def on_action(self, serv, ev, helper):
        return self.on_pubmsg(serv, ev, helper)
