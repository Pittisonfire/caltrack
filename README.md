# CalTrack - Kalorienzähler

Kalorienzähler und Ernährungstracker für 2 Benutzer.

## Features

- **Multi-User**: Einfache Benutzerauswahl (kein Passwort)
- **Lebensmittel-Suche**: Open Food Facts Datenbank (Millionen Produkte)
- **Barcode-Scanner**: Handy-Kamera zum Scannen
- **Mahlzeiten-Tracking**: Frühstück, Mittag, Abend, Snacks
- **Makros**: Kalorien, Protein, Carbs, Fett
- **Gewichtstracker**: Verlauf mit Diagramm
- **Wochenstatistik**: Übersicht der letzten 7 Tage
- **Favoriten**: Häufig genutzte Lebensmittel speichern

## Tech Stack

- **Backend**: FastAPI + PostgreSQL
- **Frontend**: React (Single HTML)
- **API**: Open Food Facts (kostenlos)
- **Scanner**: html5-qrcode Library

## Installation

```bash
cd /opt/apps
git clone https://github.com/Pittisonfire/caltrack.git
cd caltrack
docker compose up -d --build
```

## Ports

- Frontend: 8081
- Backend API: 8002

## URLs

- App: http://SERVER_IP:8081
- API Docs: http://SERVER_IP:8002/docs

## Benutzer erstellen

Beim ersten Start einfach Namen eingeben (z.B. "Peter", "Vera").

## Zukünftige Features

- [ ] Integration mit Food Planer (Rezepte als Mahlzeit loggen)
- [ ] PWA für Homescreen
- [ ] Wassertracker
- [ ] Export/Import
