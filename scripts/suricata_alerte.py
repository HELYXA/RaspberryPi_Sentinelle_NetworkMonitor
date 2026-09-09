"""
Sentinelle - Alertes Suricata
Surveille en continu le fichier de log eve.json de Suricata et envoie
une alerte Telegram a chaque nouvelle alerte detectee. Le filtre sur
"Telegram" evite une boucle infinie sur les propres requetes du bot
vers l'API Telegram.
"""

import json
import time
import requests

from config import TOKEN, CHAT_ID

EVE_LOG = "/var/log/suricata/eve.json"


def envoyer_alerte(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": message})


def suivre_log(chemin):
    with open(chemin, "r") as f:
        f.seek(0, 2)  # se placer a la fin du fichier
        while True:
            ligne = f.readline()
            if not ligne:
                time.sleep(1)
                continue
            yield ligne


if __name__ == "__main__":
    for ligne in suivre_log(EVE_LOG):
        try:
            event = json.loads(ligne)
        except json.JSONDecodeError:
            continue

        if event.get("event_type") == "alert" and "Telegram" not in event.get("alert", {}).get("signature", ""):
            envoyer_alerte(
                f"🚨 Alerte Suricata !\n"
                f"IP source: {event.get('src_ip')}\n"
                f"IP dest: {event.get('dest_ip')}\n"
                f"Signature: {event['alert'].get('signature')}\n"
                f"Sévérité: {event['alert'].get('severity')}"
            )
