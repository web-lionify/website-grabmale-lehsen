# Offene Fragen (mit Herrn Gerdes klären)

Wird ausgegeben, wenn gesagt wird: „offene Fragen beantworten“. Beantwortete Fragen hier entfernen.

## Impressum
18. Telefonnummer: Auf der Webseite steht 038852 / 509 54, im Google-Unternehmensprofil 0173 2032241. Welche Nummer soll auf die Webseite – oder beide (Festnetz und Mobil)?

## Datenschutz
13. (an Lionify) Auftragsverarbeitungsvertrag zwischen Lionify und Herrn Gerdes abschließen – danach den Satz zur Auftragsverarbeitung in der Datenschutzerklärung wieder aufnehmen.

## Inhalte
5. Steinsorten-Seite: Stimmt die Zuordnung der 6 Fotos (Orion, Himalaya, Multicolor Red, Halmstad, Viscont White, Rainbow-Sandstein)? Weitere Sorten, die vorgestellt werden sollen?
6. Liegesteine: Passt der neu geschriebene Text?
7. Hat Lehsen einen eigenen Friedhof, und wer ist Träger? (fehlt bisher bei den Friedhofssatzungen)
8. Warlitz: Laut Satzung ist die Gravur auf der Stele im anonymen Urnenfeld einem bestimmten Steinmetzbetrieb aus Hagenow zugewiesen – ist das bekannt / relevant?
19. Haus und Garten: Auf der Startseite stehen jetzt Treppen und Stufen, Fensterbänke sowie Abdeckungen und Platten. Passt die Auswahl, fehlt etwas (z. B. Küchen- oder Waschtischplatten, Hausnummern), und gibt es Fotos dazu?
9. Friedhöfe mit nicht veröffentlichten Gestaltungsvorschriften (u. a. Wittenburg, Zarrentin, Gößlow, Boizenburg-Land): Liegen Herrn Gerdes diese Vorschriften vor?

## Anfahrt
15. Gibt es Parkplätze direkt an der Ausstellung (Anzahl, Hof, Straße)?
16. Ist die Ausstellung frei zugänglich (auch außerhalb der Termine anschauen?) und barrierefrei erreichbar?
17. Gibt es einen markanten Hinweis für die Anfahrt (z. B. Schild, Hofeinfahrt, Hausfarbe) und ein Foto vom Gelände/Eingang?

## Entscheidungen
11. Google-Unternehmensprofil anlegen (Maps-Eintrag, Bewertungen)?

## Go-live (an Lionify, nicht an Herrn Gerdes)
20. Kontaktformular: Absender `MAIL_FROM` in `kontakt.php` ist noch `noreply@lionify.de`. Muss eine Adresse sein, die über das neue Hosting-Paket versenden darf (z. B. `noreply@grabmale-aus-lehsen.de`, SPF/DKIM prüfen).
21. Datenschutzerklärung, Abschnitt Hosting: nennt noch ALL-INKL. Liegt das neue Hosting-Paket dort? Sonst Anbieter anpassen (build.py).
22. grabmale.lionify.de nach dem Go-live per 301 auf grabmale-aus-lehsen.de umleiten.
23. Staging zusätzlich mit Passwortschutz (.htaccess/.htpasswd) versehen? Aktuell nur noindex + robots.txt „Disallow: /“.
