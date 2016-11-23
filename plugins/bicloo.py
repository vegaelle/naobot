# -*- coding: utf-8 -*-

from xml.etree import ElementTree

import requests

from irc3.plugins.command import command
import irc3


@irc3.plugin
class Bicloo:
    u'''Informe sur l’état du réseau de vélos Bicloo de Nantes'''

    general_url = 'http://www.bicloo.nantesmetropole.fr/service/carto'
    station_url = \
        'http://www.bicloo.nantesmetropole.fr/service/stationdetails/nantes/%d'

    def __init__(self, bot):
        self.bot = bot
        self.stations = {}
        self.stations_ids = {}
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X'
                        ' 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko)'
                        'Chrome/39.0.2171.95 Safari/537.36'}

        r = requests.get(self.general_url, headers=self.headers)
        if r.status_code is not 200:
            self.bot.log.error('Unable to access Bicloo API.')
            return
        tree = ElementTree.fromstring(r.content)
        for marker in tree.find('markers').getchildren():
            name = marker.attrib['name'][6:].lower()
            self.stations[int(marker.attrib['number'])] = name
            self.stations_ids[name] = int(marker.attrib['number'])

    def get_status(self, station_id):

        url = self.station_url % int(station_id)
        r = requests.get(url, headers=self.headers)
        if r.status_code is not 200:
            return 'Numéro de station invalide'
        tree = ElementTree.fromstring(r.content)
        station = {}
        for element in tree.getchildren():
            station[element.tag] = element.text
        if station['open'] == '0' or station['connected'] == '0':
            return 'Station indisponible'
        return u'Station %s (%d) : %d vélos sur %d disponibles' %\
            (self.stations[int(station_id)].title(), int(station_id),
             int(station['available']), int(station['total']))

    @command(permission='view')
    def bicloo(self, mask, target, args):
        """Bicloo
        Indique le nombre de vélos disponibles sur une station

            %%bicloo <station>...
        """
        cmd = ' '.join(args['<station>'])
        try:
            if cmd.isdigit():
                station_status = self.get_status(cmd)
                self.bot.privmsg(target, station_status)
            else:
                station_name = cmd
                station_id = self.stations_ids[station_name.lower()]
                station_status = self.get_status(station_id)
                yield station_status
        except:
            yield 'Station inexistante'
