# AutoDarts DartCounter Integration

Ein Python-Skript, das AutoDarts-Daten ausliest und automatisch in DartCounter einträgt.

---

## Features

* Liest die Dart-Würfe aus AutoDarts aus
* Trägt die Punkte automatisch in DartCounter ein
* Erkennt automatisch, welcher Spieler am Zug ist
* Echtzeit-Score-Updates

---

## Installation

1. **Repository von GitHub klonen**

```bash
git clone https://github.com/Ivolution-dev/dartcounter-autodarts
cd dartcounter-autodarts
```

---

2. **Virtuelle Umgebung erstellen (optional, empfohlen)**

Linux / macOS:

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

---

3. **Abhängigkeiten installieren**

```bash
pip install -r requirements.txt
```

---

4. **Konfiguration**

Öffne die Datei `dartcounter-autodarts.py` und setze deine AutoDarts-IP:

```python
AUTODARTS_URL = "http://YOUR_LOCAL_AUTODARS_IP:3180/"
```

---

5. **Skript starten**

```bash
python dartcounter-autodarts.py
```

---

## Nutzung

* Das Skript öffnet zwei Tabs im Chrome-Browser:

  * AutoDarts
  * DartCounter
* Es liest deine Dartwürfe aus AutoDarts aus und trägt sie automatisch in DartCounter ein
* Beobachte die Leg-Scores in Echtzeit im Terminal

---

## Hinweise

* Stelle sicher, dass Chrome installiert ist und der ChromeDriver zur Version deines Browsers passt
* Stoppe das Skript jederzeit mit `Ctrl+C`

---

## Enjoyen

Viel Spaß beim Spielen und Punkte sammeln! 🎯
