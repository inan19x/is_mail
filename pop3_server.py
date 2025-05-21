import socket
import threading
import os

MAILBOX_DIR = '/opt/is_mail/mailboxes'
USERS_FILE = '/opt/is_mail/users.txt'
PORT = 110

def authenticate(username, password):
    with open(USERS_FILE) as f:
        for line in f:
            user, pw = line.strip().split(':')
            if user == username and pw == password:
                return True
    return False

def handle_client(conn, addr):
    conn.send(b"+OK POP3 server ready\r\n")
    authenticated = False
    user = None

    while True:
        buffer = b""
        while b"\n" not in buffer:
            buffer += conn.recv(1024)
            data = buffer.decode().strip()

        if not data:
            break

        print(f"Client: {data}")
        if data.upper().startswith("USER"):
            user = data.split()[1]
            conn.send(b"+OK User accepted\r\n")
        elif data.upper().startswith("PASS"):
            password = data.split()[1]
            if authenticate(user, password):
                authenticated = True
                conn.send(b"+OK Authenticated\r\n")
            else:
                conn.send(b"-ERR Invalid credentials\r\n")
        elif data.upper() == "LIST" and authenticated:
            mailbox = os.path.join(MAILBOX_DIR, user)
            if not os.path.exists(mailbox):
                conn.send(b"+OK 0 messages\r\n.\r\n")
                continue
            files = os.listdir(mailbox)
            response = f"+OK {len(files)} messages\r\n"
            for i, fname in enumerate(files, start=1):
                size = os.path.getsize(os.path.join(mailbox, fname))
                response += f"{i} {size}\r\n"
            response += ".\r\n"
            conn.send(response.encode())
        elif data.upper().startswith("RETR") and authenticated:
            msg_num = int(data.split()[1])
            mailbox = os.path.join(MAILBOX_DIR, user)
            try:
                file = sorted(os.listdir(mailbox))[msg_num - 1]
                with open(os.path.join(mailbox, file), 'rb') as f:
                    content = f.read()
                conn.send(b"+OK Message follows\r\n")
                conn.send(content + b"\r\n.\r\n")
            except IndexError:
                conn.send(b"-ERR Message not found\r\n")
            except Exception as e:
                conn.send(f"-ERR {str(e)}\r\n".encode())
        elif data.upper() == "QUIT":
            conn.send(b"+OK Bye\r\n")
            break
        else:
            conn.send(b"-ERR Unknown command\r\n")
    conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', PORT))
    server.listen(5)
    print(f"POP3 Server running on port {PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    start_server()

