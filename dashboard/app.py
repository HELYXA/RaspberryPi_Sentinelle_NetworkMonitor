"""
Sentinelle - Dashboard web
Affiche les 20 dernieres alertes Suricata (rafraichi toutes les 30s) et
le playbook de reponse aux incidents. Accessible depuis le reseau local
a l'adresse http://<ip-du-pi>:5000
"""

import json
from flask import Flask, render_template

app = Flask(__name__)

EVE_LOG = "/var/log/suricata/eve.json"

PLAYBOOK = [
    {
        "menace": "Nouvel appareil inconnu",
        "actions": "Identifier le MAC, croiser avec la liste blanche, isoler si suspect, changer le mot de passe Wi-Fi",
    },
    {
        "menace": "Scan de ports",
        "actions": "Identifier l'IP source, determiner si interne ou externe, bloquer via iptables, logger l'incident",
    },
    {
        "menace": "Tentative de brute force",
        "actions": "Identifier le service cible, laisser Fail2ban agir, alerter, documenter",
    },
    {
        "menace": "Trafic anormal",
        "actions": "Capturer avec tcpdump, analyser le protocole, identifier la source, decider du blocage",
    },
]


def dernieres_alertes(nombre=20):
    alertes = []
    try:
        with open(EVE_LOG, "r") as f:
            for ligne in f:
                try:
                    event = json.loads(ligne)
                except json.JSONDecodeError:
                    continue
                if event.get("event_type") == "alert":
                    alertes.append({
                        "timestamp": event.get("timestamp"),
                        "src_ip": event.get("src_ip"),
                        "dest_ip": event.get("dest_ip"),
                        "signature": event.get("alert", {}).get("signature"),
                    })
    except FileNotFoundError:
        pass
    return alertes[-nombre:][::-1]


@app.route("/")
def index():
    return render_template("dashboard.html", alertes=dernieres_alertes(), playbook=PLAYBOOK)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
