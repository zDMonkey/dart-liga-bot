# 🎯 Dart Liga Discord Bot — Setup Anleitung

Komplette Anleitung zum Einrichten des Bots. Dauert ca. 15 Minuten, keine Programmierkenntnisse nötig.

---

## Schritt 1: Discord Bot erstellen (5 Min)

1. Geh auf https://discord.com/developers/applications
2. Klick **„New Application"** → Namen eingeben (z.B. „Dart Liga Bot")
3. Links auf **„Bot"** klicken
4. Klick **„Reset Token"** → Token kopieren und sicher speichern ⚠️
5. Aktiviere unter „Privileged Gateway Intents":
   - ✅ **Message Content Intent**
6. Links auf **„OAuth2"** → **„URL Generator"**
7. Scopes: ✅ **bot** + ✅ **applications.commands**
8. Bot Permissions: ✅ **Send Messages** + ✅ **Embed Links** + ✅ **Read Message History**
9. Generierten Link öffnen → Bot zu eurem Server hinzufügen

---

## Schritt 2: Bot hosten auf Render.com (kostenlos)

1. Geh auf https://render.com → kostenlos registrieren
2. **„New"** → **„Web Service"**
3. Wähle **„Deploy from a Git repository"**
   - Falls du kein GitHub hast: einmal kurz ein kostenloses Konto anlegen
   - Lade die 3 Dateien (bot.py, requirements.txt, liga_data.json) in ein neues Repository hoch
4. Bei Render einstellen:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
5. Unter **„Environment Variables"** → Add Variable:
   - Key: `DISCORD_TOKEN`
   - Value: Dein Bot-Token aus Schritt 1
6. **„Create Web Service"** klicken → Bot startet automatisch

---

## Schritt 3: Discord Server vorbereiten

Erstelle diese Kanäle auf eurem Server:
- `#ergebnisse` → Hier postet der Bot automatisch alle Resultate
- `#tabelle` → Optional, zum manuellen Nachschauen

---

## Schritt 4: Bot benutzen

### Ergebnis eintragen
```
/ergebnis liga:Liga 1 spieler1:Raddek legs1:9 spieler2:Schlossi legs2:5
```
→ Bot validiert automatisch ob der Score stimmt (max. Legs = First to X)
→ Postet automatisch Ergebnis + aktuelle Top 5 in #ergebnisse

### Tabelle anzeigen
```
/tabelle liga:Liga 1
```
→ Zeigt vollständige Tabelle mit allen Stats

### Spieler-Stats
```
/stats liga:Liga 2 spieler:Raddek
```
→ Zeigt Rang, Win-Rate, Leg-Differenz, letzte 5 Matches

---

## Tabellenformat erklärt

| Spalte | Bedeutung |
|--------|-----------|
| Sp | Spiele gesamt |
| S | Siege |
| N | Niederlagen |
| L+ | Legs gewonnen |
| L- | Legs verloren |
| Diff | Leg-Differenz |
| Pkt | Punkte (3 pro Sieg) |

**Sortierung:** Punkte → Leg-Differenz → Siege

---

## Häufige Fragen

**Q: Was passiert wenn jemand das falsche Ergebnis einträgt?**
A: Aktuell gibt es kein /korrektur Command — falsches Ergebnis einfach melden, dann muss die liga_data.json manuell angepasst werden. (Kann auf Wunsch als Feature ergänzt werden)

**Q: Kann der Bot auf mehreren Servern laufen?**
A: Ja, aber die Daten sind serverübergreifend in einer Datei. Für mehrere Server → separate Bots empfohlen.

**Q: Wie sichere ich die Daten?**
A: Die liga_data.json regelmäßig aus dem Render-Dashboard herunterladen oder GitHub nutzen.

---

## Ligamodus-Übersicht

| Liga | Format | First to |
|------|--------|----------|
| 🎯 Liga 1 | 501 Double Out | 9 Legs |
| 🥈 Liga 2 | 501 Double Out | 7 Legs |
| 🥉 Liga 3 | 501 Double Out | 7 Legs |
