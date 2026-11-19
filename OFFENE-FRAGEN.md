# Offene Fragen (mit Herrn Gerdes klären)

Wird ausgegeben, wenn gesagt wird: „offene Fragen beantworten“. Beantwortete Fragen hier entfernen.

## Inhalte
20. Steinsorte Atlantis (Quarzit): Woher stammt Ihr Atlantis, aus Norwegen oder aus Brasilien? Im Handel gibt es beide Herkünfte unter diesem Namen.

## Go-live (an Lionify, nicht an Herrn Gerdes)
21. Kontaktformular: Absender `MAIL_FROM` in `kontakt.php` ist noch `noreply@lionify.de`. Muss eine Adresse sein, die über das neue Hosting-Paket versenden darf (z. B. `noreply@grabmale-aus-lehsen.de`, SPF/DKIM prüfen).
22. Datenschutzerklärung, Abschnitt Hosting: nennt noch ALL-INKL. Liegt das neue Hosting-Paket dort? Sonst Anbieter anpassen (build.py).
23. grabmale.lionify.de nach dem Go-live per 301 auf grabmale-aus-lehsen.de umleiten.
24. Staging zusätzlich mit Passwortschutz (.htaccess/.htpasswd) versehen? Aktuell nur noindex + robots.txt „Disallow: /“.
