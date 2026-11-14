<?php
// Kontaktformular von grabmale.lionify.de
// Versendet die Anfrage per E-Mail. Es wird nichts auf dem Server gespeichert.

declare(strict_types=1);

const MAIL_TO   = 'steine@online.de';
const MAIL_FROM = 'noreply@lionify.de';   // Absender muss eine Adresse auf dem all-inkl-Hosting sein
const SITE_NAME = 'Grabmale aus Lehsen';
const BACK      = 'kontakt.html';

function back(string $status): void {
    header('Location: ' . BACK . '?status=' . $status . '#inhalt', true, 303);
    exit;
}

function clean(string $key, int $max): string {
    $v = isset($_POST[$key]) && is_string($_POST[$key]) ? trim($_POST[$key]) : '';
    $v = str_replace("\0", '', $v);
    return mb_substr($v, 0, $max);
}

function oneLine(string $v): string {
    return trim(preg_replace('/[\r\n\t]+/', ' ', $v));
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Location: ' . BACK, true, 303);
    exit;
}

// Spam-Schutz 1: verstecktes Feld muss leer bleiben
if (clean('website', 200) !== '') {
    back('ok'); // Bots bekommen eine Erfolgsmeldung, es wird aber nichts versendet
}

// Spam-Schutz 2: Formular darf nicht schneller als in 3 Sekunden abgeschickt werden
// und nicht älter als 24 Stunden sein
$ts = (int) clean('ts', 20);
$age = time() - $ts;
if ($ts <= 0 || $age < 3 || $age > 86400) {
    back('fehler');
}

$name    = oneLine(clean('name', 120));
$email   = oneLine(clean('email', 160));
$phone   = oneLine(clean('phone', 60));
$topic   = oneLine(clean('topic', 60));
$message = clean('message', 5000);
$consent = clean('consent', 5);

if ($name === '' || $message === '' || $consent !== '1' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    back('fehler');
}

// Spam-Schutz 3: zu viele Links in der Nachricht
if (preg_match_all('~https?://~i', $message) > 3) {
    back('fehler');
}

$subject = 'Anfrage über die Webseite: ' . ($topic !== '' ? $topic : 'Kontakt');

$body  = "Neue Anfrage über das Kontaktformular von " . SITE_NAME . "\n";
$body .= str_repeat('-', 50) . "\n\n";
$body .= "Name:    {$name}\n";
$body .= "E-Mail:  {$email}\n";
$body .= "Telefon: " . ($phone !== '' ? $phone : '–') . "\n";
$body .= "Thema:   " . ($topic !== '' ? $topic : '–') . "\n\n";
$body .= "Nachricht:\n{$message}\n\n";
$body .= str_repeat('-', 50) . "\n";
$body .= "Gesendet am " . date('d.m.Y \u\m H:i') . " Uhr. Einwilligung zur Datenverarbeitung erteilt.\n";
$body .= "Zum Antworten einfach auf diese E-Mail antworten.\n";

$encodedName = '=?UTF-8?B?' . base64_encode(SITE_NAME . ' Webseite') . '?=';
$headers = [
    'From: ' . $encodedName . ' <' . MAIL_FROM . '>',
    'Reply-To: ' . $email,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'X-Mailer: PHP',
];

$ok = mail(
    MAIL_TO,
    '=?UTF-8?B?' . base64_encode($subject) . '?=',
    $body,
    implode("\r\n", $headers),
    '-f' . MAIL_FROM
);

back($ok ? 'ok' : 'fehler');
