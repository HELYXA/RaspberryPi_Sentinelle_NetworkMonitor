# 🦋 Sentinelle - Sonde de surveillance réseau sur Raspberry Pi 5

> Un Raspberry Pi 5 transformé en sonde de surveillance réseau domestique : détection de nouveaux appareils, IDS temps réel, alertes Telegram et dashboard web.

## 🎯 Le projet

Sentinelle répond à une question : *qui est connecté sur mon réseau Wi-Fi, et comment réagir si quelque chose de suspect se produit ?*

Le système tourne 24h/24 en arrière-plan sur un Raspberry Pi 5, analyse le trafic du réseau domestique, détecte les comportements suspects et envoie des alertes en temps réel sur Telegram.

**Matériel utilisé :**
- Raspberry Pi 5 (16 Go RAM), boîtier officiel, alimentation 27W
- Atolla USB 3.0 Hub
- Raspberry Pi Camera Module 3 NoIR Wide *(prévue pour une évolution future)*

## 🧩 Architecture

```
Réseau Wi-Fi → Raspberry Pi Sentinelle → Analyse (Suricata + arp-scan) → Alertes (Telegram + Dashboard)
```

| Composant | Rôle |
|---|---|
| **arp-scan / nmap** | Découverte des appareils connectés (IP, MAC, fabricant) |
| **Suricata** | IDS - analyse le trafic en temps réel contre 50 000+ règles de sécurité |
| **Bot Telegram** | Notifications instantanées dès qu'une anomalie est détectée |
| **Dashboard Flask** | Visualisation des alertes + playbook de réponse aux incidents |
| **Fail2ban** | Bannissement automatique des IP en cas de brute-force SSH |

OS : **Raspberry Pi OS Lite 64-bit** (pas d'interface graphique, pilotage entièrement en SSH).

## 📦 Contenu du repo

```
├── scripts/
│   ├── scan_reseau.py          # Détection de nouveaux appareils + alerte Telegram
│   ├── suricata_alerte.py      # Watcher des logs Suricata + alerte Telegram
│   ├── config.example.py       # Modèle (token/chat_id réels jamais commités)
│   └── requirements.txt
├── suricata/
│   └── test.rules              # Règle de test (alerte sur ping)
├── fail2ban/
│   ├── jail.local              # Config bannissement SSH (3 échecs / 10 min → ban 1h)
│   └── telegram.conf           # Notifications Telegram sur ban/unban
├── dashboard/
│   ├── app.py                  # Application Flask
│   └── templates/dashboard.html
├── systemd/                    # Services pour démarrage automatique au boot
│   ├── sentinelle.service
│   ├── suricata-alerte.service
│   └── dashboard.service
└── docs/
    └── PROJET_RASPBERRY.pdf    # Dossier de rendu complet
```

## 🔍 Découverte réseau

`arp-scan` et `nmap` identifient les appareils connectés par IP/MAC/fabricant. Par discrétion, la surveillance passive utilise `nmap -sn` (ping simple) plutôt qu'un scan agressif - un test avec `nmap -A` a d'ailleurs déclenché une alerte ESET sur un PC du réseau, preuve que certains scans sont détectables.

**Limite connue** : les téléphones récents (iOS 14+, Android 10+) randomisent leur adresse MAC, ce qui rend leur identification peu fiable par ce seul biais.

## 🤖 Bot Telegram

Bot créé via `@BotFather` : **SentinelleLibellule_Bot** 🦋. `scripts/scan_reseau.py` scanne le réseau toutes les 30 minutes et alerte dès qu'un appareil inconnu apparaît, avec persistance de la liste connue en JSON pour survivre aux reboots.

## 🛡️ Suricata (IDS)

Déployé avec les règles **Emerging Threats Open** (50 497 règles chargées), surveille l'interface `wlan0`. `scripts/suricata_alerte.py` lit `/var/log/suricata/eve.json` en continu et relaie chaque alerte sur Telegram (avec un filtre pour éviter la boucle infinie sur ses propres notifications).

## 🖥️ Dashboard

Accessible sur le réseau local via `http://<ip-du-pi>:5000` — affiche les 20 dernières alertes Suricata (rafraîchi toutes les 30s) et un **playbook de réponse aux incidents** :

| Menace détectée | Actions à mener |
|---|---|
| Nouvel appareil inconnu | Identifier le MAC, croiser avec la liste blanche, isoler si suspect, changer le mot de passe Wi-Fi |
| Scan de ports | Identifier l'IP source, interne/externe, bloquer via iptables, logger |
| Brute force | Identifier le service ciblé, laisser Fail2ban agir, alerter, documenter |
| Trafic anormal | Capturer avec tcpdump, analyser le protocole, identifier la source, décider du blocage |

## 🔒 Fail2ban

Bannit automatiquement une IP après 3 échecs SSH en moins de 10 minutes (ban 1h), avec notification Telegram à chaque bannissement/débannissement. Testé en conditions réelles : 3 mauvais mots de passe volontaires → IP bannie + alerte reçue.

## ✅ Résultat

Sentinelle surveille le réseau domestique en continu et est capable de :
- Détecter l'arrivée d'un appareil inconnu sur le Wi-Fi
- Analyser le trafic contre 50 000+ règles de détection
- Bloquer automatiquement les tentatives de brute-force SSH
- Alerter en temps réel sur Telegram
- Centraliser tout dans un dashboard web

## 🚀 Axes d'amélioration

- Brancher le Pi en Ethernet directement sur la box pour surveiller tout le trafic du réseau (pas seulement celui du Pi)
- Intégrer la caméra NoIR pour une dimension de surveillance physique (détection de mouvement)
- Logs centralisés avec graphiques de tendance
- Réponse automatique : blocage immédiat d'une IP dès la première alerte Suricata

## 🛠️ Stack technique

`Raspberry Pi 5` `Raspberry Pi OS Lite` `Python` `Flask` `Suricata` `Fail2ban` `arp-scan` `nmap` `Telegram API` `systemd`

---

*Projet personnel - Bachelor Cybersécurité.*
