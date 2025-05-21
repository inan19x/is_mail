<?php
// index.php
define('USERS_FILE', '/opt/is_mail/users.txt');  // Path to users.txt file

// Function to authenticate against the users.txt file
function authenticate($username, $password) {
    if (!file_exists(USERS_FILE)) {
        return false;
    }

    $users = file(USERS_FILE, FILE_IGNORE_NEW_LINES);
    foreach ($users as $user) {
        list($userName, $userPassword) = explode(':', $user);
        if ($username == $userName && $password == $userPassword) {
            return true;
        }
    }
    return false;
}

// Helper to read a line from POP3 connection
function pop3_get_line($fp) {
    $line = '';
    while (!feof($fp)) {
        $line .= fgets($fp, 128);
        if (substr($line, -2) === "\r\n") break;
    }
    return $line;
}

// If the user submitted the login form
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    if (authenticate($username, $password)) {
        // Open socket to your custom POP3 server
        $fp = fsockopen("localhost", 110, $errno, $errstr, 10);
        if (!$fp) {
            echo "<p>Connection error: $errstr ($errno)</p>";
	} else {

	    echo "<h2>Welcome, $username</h2>&nbsp;[<a href=\".\">Exit</a>]";
	    echo "<hr>";

            // Read server greeting
            echo "<pre>" . htmlspecialchars(pop3_get_line($fp)) . "</pre>";

            // Send USER
            fputs($fp, "USER $username\r\n");
            echo "<pre>" . htmlspecialchars(pop3_get_line($fp)) . "</pre>";

            // Send PASS
            fputs($fp, "PASS $password\r\n");
            $response = pop3_get_line($fp);
            echo "<pre>" . htmlspecialchars($response) . "</pre>";

            if (strpos($response, '+OK') === 0) {
                // Authenticated: send LIST
                fputs($fp, "LIST\r\n");
                $list_response = '';
                while (($line = pop3_get_line($fp)) !== ".\r\n") {
                    $list_response .= $line;
                }

                // Parse LIST response
                $lines = explode("\r\n", trim($list_response));
                $messages = [];

                foreach ($lines as $line) {
                    if (preg_match('/^(\d+)\s+(\d+)$/', $line, $matches)) {
                        $messages[] = ['id' => $matches[1], 'size' => $matches[2]];
                    }
                }

                if (count($messages) > 0) {
                    echo "<h3>Read email(s) - You have " . count($messages) . " messages:</h3>";

                    foreach ($messages as $msg) {
                        fputs($fp, "RETR {$msg['id']}\r\n");
                        $message = '';
                        while (($line = pop3_get_line($fp)) !== ".\r\n") {
                            $message .= $line;
                        }

                        echo "<hr>";
                        echo "<b>Message #{$msg['id']}:</b><br>";
                        echo "<pre>" . htmlspecialchars($message) . "</pre>";
                    }
                } else {
                    echo "<h3>Read email - No emails in your inbox.</h3>";
                }
            } else {
                echo "<p>Authentication failed at POP3 server.</p>";
            }

            // Close connection
            fputs($fp, "QUIT\r\n");
            pop3_get_line($fp);
	    fclose($fp);
	    echo "<hr>";

	    include "compose.html";

        }
    } else {
        echo "<p>Invalid credentials. Please <a href=\".\">go back</a> and try again.</p>";
    }
}
if(empty($username)){
	include "login.html";
}
?>
