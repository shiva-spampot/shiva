import smtplib


SERVER = "localhost"

FROM = "sender@example.com"
TO = ["someone@example.com"]  # must be a list

SUBJECT = "Hello!"

TEXT = "This message was sent with Python's smtplib."

# Prepare actual message

message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), SUBJECT, TEXT)

# Send the mail

server = smtplib.SMTP(SERVER, 2525)
server.set_debuglevel(True)
server.sendmail(FROM, TO, message)
server.quit()
