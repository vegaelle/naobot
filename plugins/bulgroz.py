# -*- coding: utf-8 -*-

import re
from random import randint, choice
from stdPlugin import stdPlugin

class bulgroz(stdPlugin):
    u'''Implémente les plus originales phrases de spammeurs.'''

    events = {'pubmsg': {'exclusive': True},
              'action': {'exclusive': True}}

    paypal_messages = [u"C'EST OUI CONFIRMANT",
            u"VOUS ÊTES LE 10.000.00 COMPTE PAYPAL",
            u"OFFRE DU GRATUITE POUR PAIEMENT!",
            u"SVP CLIQUEZ LA CONFIRMATION POUR UN OUI",
            u"C'EST LE MESSAGE 10.00.0.000 SUR LE RÉSEAU DU CHAT SOCIALE (IRC)",
            u"POSSIBLE OBTENIR BITCOINS AVEC PARTENARIAT AMD/ATI",
            u"INSCRIVEZ-VOUS AVEC COURRIER D'ADRESSE POUR MEILLEUR DE L'OFFRE",
            u"ABLATION DU POLYPE AVEC PINCES DE CRUSTACÉ, PRÉVOYEZ PAYPAL "
            u"SI ANESTHÉSIE",
            u"SI PRIX IMPOSSIBLE DU FRAIS DE DOUANE CLIQUEZ LA CONNEXION "
            u"POUR LIVRAISON SUR VPN",
            u"C'EST OFFREMENT POUR MOINS CHER AVEC CODE 1337 SUR BOUTIQUE "
            u"PRÉVOYEZ PAYPAL",
            u"PRÉVOIR CARTE DE BANQUE POUR INSCRIVAGE EN CONNEXION DES "
            u"RENCONTRES!!"]

    cadeau_messages = [u"OBTENEZ OFFRE DE MOINS CHER POUR %(produit)s EN CLIQUANT "
            u"LE PAYPAL",
            u"%(produit)s SVP ?? ICI C'EST RÉDUCTIONS DES SOLDES SUR TOUTE LA "
            u"SEMAINE POUR LE %(produit)s",
            u"%(produit)s EXPÉDIÉ GRATUITEMENT SI COMMANDE DE LOT EN QUANTITÉ "
            u"GRANDE POUR BEAUCOUP",
            u"IL DÉSTOCKE %(produit)s SUR LA RÉGION DE VOTRE NRA OUVERT MÊME "
            u"DIMANCHE NUIT ET SHABBAT",
            u"C'EST GRAND BESOIN DE %(produit)s ???? SANS ATTENTE DEMANDEZ LIVRAISON "
            u"POUR HIER ET RECEVEZ MAINTENANT!! TRÈS RAPIDE SI PAYPAL!!",
            u"VOUS SAVEZ AVOIR BESOIN DE %(produit)s??? DONC CLIQUE VITE L'OFFRE SUR "
            u"L'ÉCRAN ET REÇOIT %(produit)s CHEZ TOI DANS VOTRE MAISON!",
            u"LA PROMOTION EST CHANCE DE VOUS POUR %(produit)s DU DISPONIBILITÉ "
            u"INSTANTANÉE!!"]

    bortz_messages = [u"BORTZ RULEZ !",
                      u"JOIN BORT'Z FANCLUB !", 
                      u"CLIQUEZ LE PAYPAL POUR ABONNEMENT GRATUIT À BLOGZMEYER SUR HTTP://WWW.BORTZMEYER.ORG !",
                      u"LES RFC SONT EN ILLIMITÉ SUR BLOGZMEYER POUR ADMINISTREMENT DES INTERNETZ !"]

    pedo = (u"PÉDO ?? CLIQUEZ POUR ICI ET DÃ‰NONCER ACTION ILLÉGALE DE "
            u"ENFANT, CLIQUEZ POUR LÀ ET OBTENIR SEXTAPE DE LA RUSSIE")
    single_answer = {
            u"tchouu": "VOYAGEZ TOUTE LA SAISON SUR LE CHEMINEMENT DE FER "
            u"GRÂCE À WEB DE BOUTIQUE POUR LES BILLETS DU WAGON",
            u"zoidberg": "PROFITEZ DE PARTENARIAT AVEC DOCTEUR DU "
            u"MOLLUSQUE ET OBTENEZ SANTÉ POUR VOUS & VOS ENFANTS & TOUTE "
            u"FAMILLE (MÊME HOMO)",
            u"pédo": pedo,
            u"pedo": pedo,
            u"bite": u"BEAUCOUP DES TAS DE MÂ©GABITES PAR MINUTES ? CLIQUEZ ICI"
                    +u" POUR LA FIBRE À CHIBRES ET ENLARGE TA PÉNICHE."
    }

    def on_pubmsg(self, serv, ev, helper):
        message = helper['message']
        long_words = re.findall(r"\b\w{7,}\b", message)

        for word in self.single_answer:
            if re.search(r"\b%s\b" % re.escape(word), message, re.I):
                serv.privmsg(helper['target'], self.single_answer[word])
                return True

        if re.search("bortz", message, re.I):
            serv.privmsg(helper['target'], choice(self.bortz_messages))
            return True

        if re.search(r"\bpaypal\b", message, re.I):
            serv.privmsg(helper['target'], choice(self.paypal_messages))
            return True

        if (long_words !=[]):
            if randint(1, 30) == 1:
                serv.privmsg(helper['target'], choice(self.cadeau_messages) % {\
                    "produit": choice(long_words).upper()})
                return True

        return False

    def on_action(self, serv, ev, helper):
        return self.on_pubmsg(serv, ev, helper)
