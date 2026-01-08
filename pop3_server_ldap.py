import socket
import threading
import os
from ldap3 import Server, Connection, ALL

MAILBOX_DIR = '/opt/is_mail/mailboxes'
PORT = 110

# LDAP configuration
LDAP_SERVER = 'win2016.acme.lab'
LDAP_PORT = 389
BASE_DN = 'dc=acme,dc=lab'


def authenticate(username, password):
    """
    Authenticate a user by attempting an LDAP bind using
    the UserPrincipalName (username@domain).
    """
    try:
        server = Server(LDAP_SERVER, port=LDAP_PORT, get_info=ALL)
        conn = Connection(
            server,
            user=username,
            password=password,
            auto_bind=True
        )
        conn.unbind()
        return True
    except Exception:
        return False


def handle_client(conn, addr):
    conn.send("+OK POP3 server ready\r\n")
    authenticated = False
    user = None

    while True:
        buffer = ""
        while "\n" not in buffer:
            data = conn.recv(1024)
            if not data:
                conn.close()
                return
            buffer += data

        data = buffer.strip()
        print("Client: {}".format(data))

        if data.upper().startswith("USER"):
            user = data.split()[1]
            conn.send("+OK User accepted\r\n")

        elif data.upper().startswith("PASS"):
            password = data.split()[1]
            if authenticate(user, password):
                authenticated = True
                conn.send("+OK Authenticated\r\n")
            else:
                conn.send("-ERR Invalid credentials\r\n")

        elif data.upper() == "LIST" and authenticated:
            mailbox = os.path.join(MAILBOX_DIR, user)
            if not os.path.exists(mailbox):
                conn.send("+OK 0 messages\r\n.\r\n")
                continue

            files = os.listdir(mailbox)
            response = "+OK {} messages\r\n".format(len(files))
            for i, fname in enumerate(files, start=1):
                size = os.path.getsize(os.path.join(mailbox, fname))
                response += "{} {}\r\n".format(i, size)
            response += ".\r\n"
            conn.send(response)

        elif data.upper().startswith("RETR") and authenticated:
            msg_num = int(data.split()[1])
            mailbox = os.path.join(MAILBOX_DIR, user)
            try:
                file = sorted(os.listdir(mailbox))[msg_num - 1]
                with open(os.path.join(mailbox, file), 'r') as f:
                    content = f.read()
                conn.send("+OK Message follows\r\n")
                conn.send(content + "\r\n.\r\n")
            except IndexError:
                conn.send("-ERR Message not found\r\n")
            except Exception as e:
                conn.send("-ERR {}\r\n".format(str(e)))

        elif data.upper() == "QUIT":
            conn.send("+OK Bye\r\n")
            break

        else:
            conn.send("-ERR Unknown command\r\n")

    conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', PORT))
    server.listen(5)
    print("POP3 Server running on port {}".format(PORT))

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == '__main__':
    start_server()

