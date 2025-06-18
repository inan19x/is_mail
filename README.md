Installation:<br>
All these scripts assumes you git clone under /opt directory, so there will be new directory called /opt/is_mail/<br>
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
You can also use telnet or netcat to interact with the server to demonstrate the basic usage of SMTP and POP3<br>
<br>
___
Example interaction with SMTP:<br><br>
_220 mail.acme.lab. Python SMTP 1.4.6_<br>
**HELO acme.lab**<br>
_250 mail.acme.lab._<br>
**MAIL FROM: bob@acme.lab**<br>
_250 OK_<br>
**RCPT TO: alice@acme.lab**<br>
_250 OK_<br>
**DATA**<br>
_354 End data with &lt;CR&gt;&lt;LF&gt;.&lt;CR&gt;&lt;LF&gt;_<br>
**Subject: Hi, Alice!<br>
Dear Alice,<br>
How are you?<br>
<br>
Regards,<br>
Bob<br>
.**<br>
_250 OK_<br>
**QUIT**<br>
_221 Bye_<br>
<br>
___
Example interaction with POP3:<br><br>
_+OK POP3 server ready_<br>
**USER alice@acme.lab**<br>
_+OK User accepted_<br>
**PASS Adms1234**<br>
_+OK Authenticated_<br>
**LIST**<br>
_+OK 1 messages_<br>
_1 329_<br>
_._<br>
**RETR 1**<br>
_+OK Message follows_<br>
_Subject: Hi, Alice!_<br>
_X-Peer: ('172.27.32.1', 7794)_<br>
_X-MailFrom: bob@acme.lab_<br>
_X-RcptTo: alice@acme.lab_<br>
<br>
_Dear Alice,_<br>
_How are you?_<br>
<br>
_Regards,_<br>
_Bob_<br>
<br>
_._<br>
**QUIT**<br>
_+OK Bye_<br>
