# -*- coding: utf-8 -*-

from stdPlugin import stdPlugin
from xml.etree import ElementTree
import requests

class bicloo(stdPlugin):
    u'''Informe sur l’état du réseau de vélos Bicloo de Nantes'''

    events = {'pubmsg': {'exclusive': True, 'command_namespace': 'bicloo'}}

    general_url = 'http://www.bicloo.nantesmetropole.fr/service/carto'
    station_url = 'http://www.bicloo.nantesmetropole.fr/service/stationdetails/nantes/%d'

    def __init__(self, *args, **kwargs):
        self.stations = {}
        self.stations_ids = {}
        r = requests.get(self.general_url)
        if r.status_code is not 200:
            raise PluginError('Unable to access Bicloo API.')
        tree = ElementTree.fromstring(r.content)
        for marker in tree.find('markers').getchildren():
            name = marker.attrib['name'][6:].lower()
            self.stations[int(marker.attrib['number'])] = name
            self.stations_ids[name] = int(marker.attrib['number'])
        return super(bicloo, self).__init__(*args, **kwargs)

    def get_status(self, id):

        url = self.station_url % int(id)
        r = requests.get(url)
        if r.status_code is not 200:
            return 'Numéro de station invalide'
        tree = ElementTree.fromstring(r.content)
        station = {}
        for element in tree.getchildren():
            station[element.tag] = element.text
        if station['open'] == '0' or station['connected'] == '0':
            return 'Station indisponible'
        return u'Station %s (%d) : %d vélos sur %d disponibles' %\
            (self.stations[int(id)].title(), int(id), int(station['available']), int(station['total']))


    def on_cmd(self, serv, ev, command, args, helper):
        u'''%(namespace)s <ID> : Indique le statut de la station <ID>
        %(namespace)s <nom> : Indique le statut de la station <nom>'''
        if command.isdigit():
            station_status = self.get_status(command)
            serv.privmsg(helper['target'], station_status)
        else:
            args.insert(0, command)
            station_name = ' '.join(args)
            station_id = self.stations_ids[station_name.lower()]
            station_status = self.get_status(station_id)
            serv.privmsg(helper['target'], station_status)
        return True
