# -*- coding: utf-8 -*-

from stdPlugin import stdPlugin
import re

class bulgroz(stdPlugin):
    u'''Implémente les plus originales phrases de spammeurs.'''

    events = {'pubmsg': {'exclusive': True},
              'action': {'exclusive': True}}

    paypal_messages = ["C'EST OUI CONFIRMANT",
            "VOUS ÊTES LE 10.000.00 COMPTE PAYPAL",
            "OFFRE DU GRATUITE POUR PAIEMENT!",
            "SVP CLIQUEZ LA CONFIRMATION POUR UN OUI",
            "C'EST LE MESSAGE 10.00.0.000 SUR LE RÉSEAU DU CHAT SOCIALE (IRC)",
            "POSSIBLE OBTENIR BITCOINS AVEC PARTENARIAT AMD/ATI",
            "INSCRIVEZ-VOUS AVEC COURRIER D'ADRESSE POUR MEILLEUR DE L'OFFRE",
            "ABLATION DU POLYPE AVEC PINCES DE CRUSTACÉ, PRÉVOYEZ PAYPAL "
            "SI ANESTHÉSIE",
            "SI PRIX IMPOSSIBLE DU FRAIS DE DOUANE CLIQUEZ LA CONNEXION "
            "POUR LIVRAISON SUR VPN",
            "C'EST OFFREMENT POUR MOINS CHER AVEC CODE 1337 SUR BOUTIQUE "
            "PRÉVOYEZ PAYPAL",
            "PRÉVOIR CARTE DE BANQUE POUR INSCRIVAGE EN CONNEXION DES "
            "RENCONTRES!!"]

    cadeau_messages = ["OBTENEZ OFFRE DE MOINS CHER POUR %s EN CLIQUANT "
            "LE PAYPAL",
            "%s SVP ?? ICI C'EST RÉDUCTIONS DES SOLDES SUR TOUTE LA "
            "SEMAINE POUR LE %s",
            "%s EXPÉDIÉ GRATUITEMENT SI COMMANDE DE LOT EN QUANTITÉ "
            "GRANDE POUR BEAUCOUP",
            "IL DÉSTOCKE %s SUR LA RÉGION DE VOTRE NRA OUVERT MÊME "
            "DIMANCHE NUIT ET SHABBAT",
            "C'EST GRAND BESOIN DE %s ???? SANS ATTENTE DEMANDEZ LIVRAISON "
            "POUR HIER ET RECEVEZ MAINTENANT!! TRÈS RAPIDE SI PAYPAL!!",
            "VOUS SAVEZ AVOIR BESOIN DE %s??? DONC CLIQUE VITE L'OFFRE SUR "
            "L'ÉCRAN ET REÇOIT %s CHEZ TOI DANS VOTRE MAISON!",
            "LA PROMOTION EST CHANCE DE VOUS POUR %s DU DISPONIBILITÉ "
            "INSTANTANÉE!!"]

    bortz_messages = ["BORTZ RULEZ !",
                      "JOIN BORT'Z FANCLUB !", 
                      "CLIQUEZ LE PAYPAL POUR ABONNEMENT GRATUIT À BLOGZMEYER SUR HTTP://WWW.BORTZMEYER.ORG !",
                      "LES RFC SONT EN ILLIMITÉ SUR BLOGZMEYER POUR ADMINISTREMENT DES INTERNETZ !"]

    pedo = ("PÉDO ?? CLIQUEZ POUR ICI ET DÃ‰NONCER ACTION ILLÉGALE DE "
            "ENFANT, CLIQUEZ POUR LÀ ET OBTENIR SEXTAPE DE LA RUSSIE")
    single_answer = {
            "coin": "pan",
            "nioc": "nap",
            "tchouu": "VOYAGEZ TOUTE LA SAISON SUR LE CHEMINEMENT DE FER "
            "GRÂCE À WEB DE BOUTIQUE POUR LES BILLETS DU WAGON",
            "zoidberg": "PROFITEZ DE PARTENARIAT AVEC DOCTEUR DU "
            "MOLLUSQUE ET OBTENEZ SANTÉ POUR VOUS & VOS ENFANTS & TOUTE "
            "FAMILLE (MÊME HOMO)",
            "pédo": pedo,
            "pedo": pedo,
    }

    def on_pubmsg(self, serv, ev, helper):
        message = helper['message']
        long_words = re.findall(r"\b\w{8,}\b", message)

        for word in single_answer:
            if re.search(r"\b%s\b" % re.escape(word), message, re.I):
                serv.privmsg(helper['target'], self.single_answer[word])
                return True

        if re.search("bortz", message, re.I):
            serv.privmsg(helper['target'], choice(self.bortz_messages))
            return True

        if re.search(r"\bpaypal\b", message, re.I):
            serv.privmsg(helper['target'], choice(self.paypal_messages))
            return True

        return False

    def on_action(self, serv, ev, helper):
        return self.on_pubmsg(serv, ev, helper)
