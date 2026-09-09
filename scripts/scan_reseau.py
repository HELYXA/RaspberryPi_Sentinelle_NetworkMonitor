"""
Sentinelle - Surveillance reseau
Scanne le reseau local toutes les 30 minutes via arp-scan et envoie une
alerte Telegram dès qu'un appareil inconnu est detecte. La liste des
appareils connus est persistee dans un fichier JSON pour survivre aux
redemarrages du Pi.
"""

import requests
import subprocess
import time
import json
import os

from config import TOKEN, CHAT_ID

DEVICES_FILE = "appareils_connus.json"


def envoyer_alerte(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": message})


def charger_appareils_connus():
    if os.path.exists(DEVICES_FILE):
        with open(DEVICES_FILE, "r") as f:
            return set(tuple(a) for a in json.load(f))
    return set()


def sauvegarder_appareils_connus(appareils):
    with open(DEVICES_FILE, "w") as f:
        json.dump(list(appareils), f)


def scanner_reseau():
    result = subprocess.run(
        ["sudo", "arp-scan", "--localnet", "--ouifile=/tmp/ieee-oui.txt"],
        capture_output=True, text=True
    )

    appareils = set()
    for ligne in result.stdout.split("\n"):
        if "192.168." in ligne:
            parts = ligne.split()
            if len(parts) >= 3:
                appareils.add((parts[0], parts[1], parts[2]))
            elif len(parts) == 2:
                appareils.add((parts[0], parts[1], "Inconnu"))
    return appareils


if __name__ == "__main__":
    appareils_connus = charger_appareils_connus()

    while True:
        appareils = scanner_reseau()
        for appareil in appareils:
            if appareil not in appareils_connus:
                appareils_connus.add(appareil)
                sauvegarder_appareils_connus(appareils_connus)
                envoyer_alerte(
                    f"⚠️ Nouvel appareil détecté !\n"
                    f"IP: {appareil[0]}\n"
                    f"MAC: {appareil[1]}\n"
                    f"Fabricant: {appareil[2]}"
                )
        time.sleep(1800)
