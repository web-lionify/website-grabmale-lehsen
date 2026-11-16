<?php
// Kontaktformular von grabmale.lionify.de
// Versendet die Anfrage per E-Mail. Es wird nichts auf dem Server gespeichert.

declare(strict_types=1);

const MAIL_TO   = 'steine@online.de';
const MAIL_FROM = 'noreply@lionify.de';   // Absender muss eine Adresse auf dem all-inkl-Hosting sein
const SITE_NAME = 'Grabmale aus Lehsen';
const BACK      = 'kontakt.html';

// Vorlage der HTML-Mail (Tabellen und Inline-Stile, damit sie in allen Mailprogrammen gleich aussieht)
const MAIL_TEMPLATE = <<<'HTML'
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>Neue Anfrage</title>
</head>
<body style="margin:0;padding:0;background:#f2f3f4;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:#f2f3f4;">{{preheader}}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f2f3f4;">
<tr><td align="center" style="padding:32px 12px;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;background:#ffffff;border:1px solid #d5d9dd;border-radius:6px;">
    <tr><td style="background:#2c3238;padding:26px 32px;border-radius:6px 6px 0 0;">
      <div style="font:400 24px/1.2 Georgia,'Palatino Linotype',Palatino,serif;color:#ffffff;">{{site}}</div>
      <div style="font:600 11px/1.4 Arial,Helvetica,sans-serif;letter-spacing:2px;text-transform:uppercase;color:#b8bfc6;margin-top:6px;">Kontaktformular der Webseite</div>
    </td></tr>
    <tr><td style="padding:30px 32px 8px;font-family:Arial,Helvetica,sans-serif;color:#1d2125;">
      <div style="font:600 11px/1.4 Arial,Helvetica,sans-serif;letter-spacing:2px;text-transform:uppercase;color:#56687a;">Neue Anfrage</div>
      <div style="font:400 26px/1.25 Georgia,'Palatino Linotype',Palatino,serif;color:#1d2125;margin:6px 0 0;">{{topic}}</div>
    </td></tr>
    <tr><td style="padding:18px 32px 0;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font:15px/1.5 Arial,Helvetica,sans-serif;color:#1d2125;border-top:1px solid #d5d9dd;">
        <tr><td width="90" style="padding:11px 12px 11px 0;border-bottom:1px solid #e6e8ea;color:#4f565d;font-size:13px;vertical-align:top;">Name</td><td style="padding:11px 0;border-bottom:1px solid #e6e8ea;font-weight:bold;">{{name}}</td></tr>
        <tr><td width="90" style="padding:11px 12px 11px 0;border-bottom:1px solid #e6e8ea;color:#4f565d;font-size:13px;vertical-align:top;">E-Mail</td><td style="padding:11px 0;border-bottom:1px solid #e6e8ea;"><a href="mailto:{{email}}" style="color:#3e4e5e;text-decoration:underline;">{{email}}</a></td></tr>
        <tr><td width="90" style="padding:11px 12px 11px 0;border-bottom:1px solid #e6e8ea;color:#4f565d;font-size:13px;vertical-align:top;">Telefon</td><td style="padding:11px 0;border-bottom:1px solid #e6e8ea;">{{phone}}</td></tr>
      </table>
    </td></tr>
    <tr><td style="padding:26px 32px 0;font-family:Arial,Helvetica,sans-serif;">
      <div style="font:600 11px/1.4 Arial,Helvetica,sans-serif;letter-spacing:2px;text-transform:uppercase;color:#4f565d;margin-bottom:10px;">Nachricht</div>
      <div style="background:#f2f3f4;border-left:3px solid #56687a;padding:16px 18px;font:15px/1.65 Arial,Helvetica,sans-serif;color:#1d2125;">{{message}}</div>
    </td></tr>
    <tr><td style="padding:28px 32px 32px;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td style="background:#2c3238;border-radius:4px;">
        <a href="{{reply}}" style="display:inline-block;padding:13px 24px;font:600 15px/1 Arial,Helvetica,sans-serif;color:#ffffff;text-decoration:none;">Antworten</a>
      </td></tr></table>
      <div style="font:13px/1.5 Arial,Helvetica,sans-serif;color:#4f565d;margin-top:12px;">Oder einfach im Mailprogramm auf „Antworten“ klicken – die Antwort geht direkt an den Absender.</div>
    </td></tr>
    <tr><td style="background:#e6e8ea;padding:16px 32px;border-radius:0 0 6px 6px;font:12px/1.5 Arial,Helvetica,sans-serif;color:#4f565d;">
      Gesendet am {{sent}} über grabmale.lionify.de. Die Einwilligung zur Datenverarbeitung wurde erteilt.
    </td></tr>
  </table>
</td></tr>
</table>
</body>
</html>
HTML;

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

date_default_timezone_set('Europe/Berlin');
$sentAt = date('d.m.Y \u\m H:i') . ' Uhr';

// Textfassung (für Mailprogramme ohne HTML-Anzeige)
$text  = "Neue Anfrage über das Kontaktformular von " . SITE_NAME . "\n";
$text .= str_repeat('-', 50) . "\n\n";
$text .= "Name:    {$name}\n";
$text .= "E-Mail:  {$email}\n";
$text .= "Telefon: " . ($phone !== '' ? $phone : '–') . "\n";
$text .= "Thema:   " . ($topic !== '' ? $topic : '–') . "\n\n";
$text .= "Nachricht:\n{$message}\n\n";
$text .= str_repeat('-', 50) . "\n";
$text .= "Gesendet am {$sentAt}. Einwilligung zur Datenverarbeitung erteilt.\n";
$text .= "Zum Antworten einfach auf diese E-Mail antworten.\n";

// HTML-Fassung
function h(string $v): string {
    return htmlspecialchars($v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

$phoneHtml = '–';
if ($phone !== '') {
    $tel = (string) preg_replace('/[^0-9+]/', '', $phone);
    $phoneHtml = $tel !== ''
        ? '<a href="tel:' . h($tel) . '" style="color:#3e4e5e;text-decoration:underline;">' . h($phone) . '</a>'
        : h($phone);
}
$replyHref = 'mailto:' . h($email) . '?subject=' . rawurlencode('Ihre Anfrage bei ' . SITE_NAME);

$html = strtr(MAIL_TEMPLATE, [
    '{{site}}'      => h(SITE_NAME),
    '{{preheader}}' => h($name . ' – ' . ($topic !== '' ? $topic : 'Kontakt')),
    '{{topic}}'     => h($topic !== '' ? $topic : 'Kontakt'),
    '{{name}}'      => h($name),
    '{{email}}'     => h($email),
    '{{phone}}'     => $phoneHtml,
    '{{message}}'   => nl2br(h($message)),
    '{{reply}}'     => $replyHref,
    '{{sent}}'      => h($sentAt),
]);

$boundary = 'grabmale-' . bin2hex(random_bytes(12));
$body  = "This is a multi-part message in MIME format.\r\n\r\n";
$body .= "--{$boundary}\r\n";
$body .= "Content-Type: text/plain; charset=UTF-8\r\n";
$body .= "Content-Transfer-Encoding: base64\r\n\r\n";
$body .= chunk_split(base64_encode($text)) . "\r\n";
$body .= "--{$boundary}\r\n";
$body .= "Content-Type: text/html; charset=UTF-8\r\n";
$body .= "Content-Transfer-Encoding: base64\r\n\r\n";
$body .= chunk_split(base64_encode($html)) . "\r\n";
$body .= "--{$boundary}--\r\n";

$encodedName = '=?UTF-8?B?' . base64_encode(SITE_NAME . ' Webseite') . '?=';
$headers = [
    'From: ' . $encodedName . ' <' . MAIL_FROM . '>',
    'Reply-To: ' . $email,
    'MIME-Version: 1.0',
    'Content-Type: multipart/alternative; boundary="' . $boundary . '"',
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
