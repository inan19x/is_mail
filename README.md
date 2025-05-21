File descriptions:

systemd/mypop3.service - service file for systemd, to support run the pop3 service using systemctl
systemd/mysmtp.service - service file for systemd, to support run the smtp service using systemctl
pop3_server.py - the actual pop3 server, require python3
smtp_server.py - the actual smtp server, require python3
users.txt - list of users and its default password (yes, you can change it)
mailboxes/* - email storage for the users
webmail/* - host these files in your web server directory e.g /var/www/html and start to use webmail through your browser

Of course you can also use telnet or netcat to interact with the server to demonstrate the basic usage of SMTP and POP3
