# ZDFheute 🧡 ZDF Digital | WhatsApp Artikel-Checker

Ein internes Tool zum Abgleich von ZDFheute-Artikeln mit dem WhatsApp-Kanal.

## 🎯 Funktion

Die App prüft, welche Artikel von `zdfheute.de` / `heute.de` aus einer hochgeladenen
Piano-Excel-Datei **bereits** im WhatsApp-Kanal veröffentlicht wurden – und welche **noch nicht**.

## 🚀 Deployment

### Option 1: Streamlit Cloud (empfohlen)

1. Forke dieses Repository auf GitHub
2. Gehe zu [share.streamlit.io](https://share.streamlit.io)
3. Verbinde dein GitHub-Konto
4. Wähle `app.py` als Hauptdatei
5. Deploy 🎉

### Option 2: Docker

```bash
docker build -t zdf-checker .
docker run -p 8501:8501 zdf-checker
```

Dann öffne [http://localhost:8501](http://localhost:8501)

### Option 3: Lokal ausführen

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📋 Excel-Format

Die hochgeladene Excel-Datei muss eine Spalte **`URL`** enthalten (standardmäßig in Spalte D).
Darunter befinden sich alle Artikel-URLs aus dem Piano-System.

## 🔍 Wie die App funktioniert

1. **Excel-Upload**: Lade die Piano-Export-Datei hoch
2. **Datumsfilter**: Wähle den gewünschten Zeitraum
3. **Scraping**: Die App durchsucht ZDF-Sitemaps und Kategorie-Seiten
4. **Abgleich**: Excel-URLs werden mit gefundenen ZDF-Artikeln verglichen
5. **Ergebnisse**: Zwei Listen – veröffentlicht / nicht veröffentlicht

## 📁 Projektstruktur

```
├── app.py              # Haupt-App
├── requirements.txt    # Python-Abhängigkeiten
├── Dockerfile          # Docker-Konfiguration
├── .streamlit/
│   └── config.toml     # Streamlit-Konfiguration
└── README.md
```

## 🎨 Tech Stack

- **Python 3.11+**
- **Streamlit** – Web-Framework
- **pandas** – Datenverarbeitung
- **requests + BeautifulSoup4** – Web Scraping
- **openpyxl** – Excel-Verarbeitung
- **lxml** – XML/Sitemap-Parsing

## 🧡 Kontakt

Feedback an: Matthias Schmickl
