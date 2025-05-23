<?php

function sendSMTPMail($from, $to, $subject, $body) {
    $smtp_host = 'localhost';
    $smtp_port = 25;

    $socket = fsockopen($smtp_host, $smtp_port, $errno, $errstr, 10);
    if (!$socket) {
        echo "Connection failed: $errstr ($errno)";
        return false;
    }

    // Helper to read server response
    function get_response($socket) {
        $response = '';
        while ($line = fgets($socket, 515)) {
            $response .= $line;
            if (substr($line, 3, 1) === ' ') {
                break;
            }
        }
        return $response;
    }

    // Helper to send a command and get response
    function send_cmd($socket, $cmd) {
        fwrite($socket, $cmd . "\r\n");
        return get_response($socket);
    }

    get_response($socket); // Read initial server response

    send_cmd($socket, "HELO localhost");
    send_cmd($socket, "MAIL FROM:<$from>");
    send_cmd($socket, "RCPT TO:<$to>");
    send_cmd($socket, "DATA");

    // Construct headers and message
    $headers  = "From: $from\r\n";
    $headers .= "To: $to\r\n";
    $headers .= "Subject: $subject\r\n";
    $headers .= "X-Mailer: PHP/" . phpversion() . "\r\n";

    $message = $headers . "\r\n" . $body . "\r\n.";

    send_cmd($socket, $message);
    send_cmd($socket, "QUIT");

    fclose($socket);
    return true;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $from = $_POST['from_email'];
    $to = $_POST['to_email'];
    $subject = $_POST['subject'];
    $body = $_POST['body'];

    if (sendSMTPMail($from, $to, $subject, $body)) {
	echo "<div align=\"center\" style=\"background-color:#00ff00; font-size:20px;\">Email sent successfully! [<a href=\".\">Exit</a>]</div>";
    } else {
	echo "<div align=\"center\" style=\"background-color:#ff0000; font-size:20px;\">Failed to send email. [<a href=\".\">Exit</a>]</div>";
    }
}
?>

