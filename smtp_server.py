import asyncio
import os
from email.message import EmailMessage
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import AsyncMessage

MAILBOX_DIR = '/opt/is_mail/mailboxes'
USERS_FILE = '/opt/is_mail/users.txt'
PORT = 25

def user_exists(username):
    if not os.path.exists(USERS_FILE):
        return False
    with open(USERS_FILE) as f:
        return any(line.split(':')[0] == username for line in f)


class CustomSMTPHandler(AsyncMessage):
    async def handle_message(self, message: EmailMessage):
        subject = message['Subject']
        mailfrom = message['X-MailFrom']
        rcpttos = message.get_all('X-RcptTo', [])
        print(f"Sending email \"{subject}\" from: {mailfrom} to: {rcpttos}")

        for rcpt in rcpttos:
            username = rcpt.split()[0]
            if not user_exists(username):
                print(f"User {username} not found, discarding email.")
                continue

            user_mailbox = os.path.join(MAILBOX_DIR, username)
            os.makedirs(user_mailbox, exist_ok=True)
            message_count = len(os.listdir(user_mailbox)) + 1
            with open(os.path.join(user_mailbox, f"{message_count}.txt"), 'w') as f:
                f.write(message.as_string())


if __name__ == '__main__':
    handler = CustomSMTPHandler()
    controller = Controller(handler, hostname='0.0.0.0', port=PORT)
    controller.start()
    print(f"SMTP Server running on port {PORT}")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()
