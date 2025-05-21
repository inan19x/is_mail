Installation:<br>
All these scripts assumes you git clone this file under /opt directory, so there will be new directory called /opt/is_mail/<br>
<br>
File descriptions:<br>
-systemd/mypop3.service - service file for systemd, to support run the pop3 service using systemctl<br>
-systemd/mysmtp.service - service file for systemd, to support run the smtp service using systemctl<br>
-pop3_server.py - the actual pop3 server, require python3<br>
-smtp_server.py - the actual smtp server, require python3<br>
-users.txt - list of users and its default password (yes, you can change it)<br>
-mailboxes/* - email storage for the users<br>
-webmail/* - host these files in your web server directory e.g /var/www/html and start to use webmail through your browser<br>
<br>
You can also use telnet or netcat to interact with the server to demonstrate the basic usage of SMTP and POP3
