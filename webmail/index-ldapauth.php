<?php
// index.php
// LDAP configuration
define('LDAP_SERVER', 'ldap://win2016.acme.lab:389');
define('BASE_DN', 'dc=acme,dc=lab');

// Non-anonymous bind with service account, example: "MySvc Account" (password: Secret1234)
define('LDAP_BIND_USER', 'CN=MySvc Account,CN=Users,DC=ACME,DC=LAB');
define('LDAP_BIND_PASS', 'Secret1234');

function authenticate($username, $password) {
    // Only allow userPrincipalName format
    if (strpos($username, '@') === false) {
        return false; // reject short usernames
    }

    $ldap = ldap_connect(LDAP_SERVER);
    if (!$ldap) {
        return false;
    }

    ldap_set_option($ldap, LDAP_OPT_PROTOCOL_VERSION, 3);
    ldap_set_option($ldap, LDAP_OPT_REFERRALS, 0);

    // Step 1: Bind with service account
    if (!@ldap_bind($ldap, LDAP_BIND_USER, LDAP_BIND_PASS)) {
        ldap_close($ldap);
        return false;
    }

    // Step 2: Search for user by userPrincipalName
    $filter = '(userPrincipalName=' . ldap_escape($username, '', 0) . ')';
    $search = ldap_search($ldap, BASE_DN, $filter);
    if (!$search) {
        ldap_close($ldap);
        return false;
    }

    $entries = ldap_get_entries($ldap, $search);
    if ($entries['count'] == 0) {
        ldap_close($ldap);
        return false;
    }

    // Step 3: Get the full DN
    $user_dn = $entries[0]['distinguishedname'][0];
    ldap_close($ldap); // close service account bind

    // Step 4: Bind with user's DN and password
    $ldap2 = ldap_connect(LDAP_SERVER);
    ldap_set_option($ldap2, LDAP_OPT_PROTOCOL_VERSION, 3);
    ldap_set_option($ldap2, LDAP_OPT_REFERRALS, 0);

    $bind = @ldap_bind($ldap2, $user_dn, $password);
    ldap_close($ldap2);

    return $bind ? true : false;
}

/**
 * Simple helper for escaping LDAP filters (PHP < 5.6 does not have ldap_escape)
 */
function ldap_escape($str, $ignore = '', $flags = 0) {
    $metaChars = array('\\', '*', '(', ')', "\x00");
    $quotedMetaChars = array();
    foreach ($metaChars as $key => $char) {
        if (strpos($ignore, $char) === false) {
            $quotedMetaChars[$key] = '\\' . str_pad(dechex(ord($char)), 2, '0', STR_PAD_LEFT);
        } else {
            $quotedMetaChars[$key] = $char;
        }
    }
    return str_replace($metaChars, $quotedMetaChars, $str);
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

	    echo "<div align=\"center\" style=\"background-color:#80b0ff; font-size:25px;\">Welcome, $username</h2>&nbsp;[<a href=\".\">Exit</a>]</div>";

	    echo "<div style=\"background-color:#e0e0e0;\">";

            // Read server greeting
            echo "<pre>" . htmlspecialchars(pop3_get_line($fp)) . "</pre>";

            // Send USER
            fputs($fp, "USER $username\r\n");
            echo "<pre>" . htmlspecialchars(pop3_get_line($fp)) . "</pre>";

            // Send PASS
            fputs($fp, "PASS $password\r\n");
            $response = pop3_get_line($fp);
            echo "<pre>" . htmlspecialchars($response) . "</pre>";

	    echo "</div>";
	    echo "<hr>";

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
			$message=nl2br($message);
			echo "<p style=\"padding:5px;background-color:#f0f0f0;font-family:'Courier New';font-size:12px;\">" . $message . "</p>";
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

	    include "compose.php";

	    echo "<div align=\"center\" style=\"background-color:#80b0ff; font-size:25px;\">mySimple&trade; webmail</div>";

        }
    } else {
	echo "<div align=\"center\" style=\"background-color:#ff8a8a; font-size:20px;\">Invalid credentials. Please <a href=\".\">go back</a> and try again.</p></div>";

    }
}
if(empty($username)){
	include "login.php";
}
?>
