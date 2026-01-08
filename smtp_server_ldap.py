import socket
import threading
import os
from ldap3 import Server, Connection, ALL, SUBTREE

MAILBOX_DIR = '/opt/is_mail/mailboxes'
PORT = 25

# LDAP configuration
LDAP_SERVER = 'win2016.acme.lab'
LDAP_PORT = 389
BASE_DN = 'dc=acme,dc=lab'


def user_exists(username):
    """
    Check if a user exists in LDAP by searching for UserPrincipalName=username.
    Returns True if found, False otherwise.
    """
    try:
        server = Server(LDAP_SERVER, port=LDAP_PORT, get_info=ALL)
        # Non-anonymous bind with service account, example: "MySvc Account" (password: Secret1234)
        conn = Connection(server, user='CN=MySvc Account,CN=Users,DC=acme,DC=lab', password='Secret1234', auto_bind=True)
        # Search for user with the exact UserPrincipalName
        conn.search(
            search_base=BASE_DN,
            search_filter='(userPrincipalName={})'.format(username),
            search_scope=SUBTREE,
            attributes=['userPrincipalName']
        )
        found = len(conn.entries) > 0
        conn.unbind()
        return found
    except Exception as e:
        print("LDAP search error for {}: {}".format(username, str(e)))
        return False


def handle_client(conn, addr):
    conn.send("+OK SMTP server - centos7.acme.lab\r\n")
    sender = None
    recipients = []
    data_mode = False
    data_lines = []

    while True:
        if not data_mode:
            buffer = ""
            while "\n" not in buffer:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                buffer += chunk.decode()
            if not buffer:
                break
            data = buffer.strip()
            print("Client:", data)

            cmd = data.split()[0].upper()
            if cmd == "HELO" or cmd == "EHLO":
                conn.send("250 Hello\r\n")
            elif cmd == "MAIL":
                if data.upper().startswith("MAIL FROM:"):
                    sender_addr = data[10:].strip()
                    if sender_addr.startswith("<") and sender_addr.endswith(">"):
                        sender_addr = sender_addr[1:-1]
                    sender = sender_addr
                    conn.send("250 OK\r\n")
                else:
                    conn.send("500 Syntax error in MAIL command\r\n")
            elif cmd == "RCPT":
                if data.upper().startswith("RCPT TO:"):
                    recipient_addr = data[8:].strip()
                    if recipient_addr.startswith("<") and recipient_addr.endswith(">"):
                        recipient_addr = recipient_addr[1:-1]

                    if user_exists(recipient_addr):
                        recipients.append(recipient_addr)
                        conn.send("250 OK\r\n")
                    else:
                        conn.send("550 No such user here\r\n")
                else:
                    conn.send("500 Syntax error in RCPT command\r\n")
            elif cmd == "DATA":
                if not sender or not recipients:
                    conn.send("503 Bad sequence of commands\r\n")
                else:
                    conn.send("354 End data with <CR><LF>.<CR><LF>\r\n")
                    data_mode = True
                    data_lines = []
            elif cmd == "RSET":
                sender = None
                recipients = []
                data_mode = False
                data_lines = []
                conn.send("250 OK\r\n")
            elif cmd == "NOOP":
                conn.send("250 OK\r\n")
            elif cmd == "QUIT":
                conn.send("221 Bye\r\n")
                break
            else:
                conn.send("502 Command not implemented\r\n")
        else:
            line = ""
            while True:
                chunk = conn.recv(1)
                if not chunk:
                    break
                line += chunk.decode()
                if line.endswith("\n"):
                    break

            if not line:
                break

            line_str = line.strip("\r\n")
            if line_str == ".":
                data_mode = False

                # Prepare headers
                peer_header = "X-Peer: {}".format(addr[0])
                mailfrom_header = "X-MailFrom: {}".format(sender)
                rcptto_header = "X-RcptTo: {}".format(", ".join(recipients))

                # Prepend headers to the message
                full_message_lines = [peer_header, mailfrom_header, rcptto_header] + data_lines

                for recipient in recipients:
                    mailbox_path = os.path.join(MAILBOX_DIR, recipient)
                    if not os.path.exists(mailbox_path):
                        os.makedirs(mailbox_path)

                    try:
                        existing = os.listdir(mailbox_path)
                    except OSError:
                        existing = []
                    msg_num = len(existing) + 1
                    filename = os.path.join(mailbox_path, "{}.txt".format(msg_num))
                    with open(filename, "w") as f:
                        f.write("\r\n".join(full_message_lines))

                sender = None
                recipients = []
                data_lines = []
                conn.send("+OK Message received\r\n")
            else:
                # Handle dot-stuffing (lines starting with a dot have one dot removed)
                if line_str.startswith("."):
                    line_str = line_str[1:]
                data_lines.append(line_str)

    conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', PORT))
    server.listen(5)
    print("SMTP Server running on port {}".format(PORT))

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == '__main__':
    start_server()

