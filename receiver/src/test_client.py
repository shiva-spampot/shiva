import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Email credentials
sender_email = "your_email@example.com"
receiver_email = "receiver_email@example.com"
username = "username"  # Your email address
password = "password"

# SMTP server details
smtp_server = "localhost"
smtp_port = 2525  # or 465 for SSL

# Create the MIMEMultipart message object
msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = "Subject of the email"

# Body of the email
body = "Hello, this is the body of the email."
msg.attach(MIMEText(body, "plain"))

# Path to the attachment
file_path = ""  # replace with your file path

# Attach the file
# Uncomment below code to send attachment
# with open(file_path, "rb") as attachment:
#     part = MIMEBase("application", "octet-stream")
#     part.set_payload(attachment.read())
#     encoders.encode_base64(part)  # Encode the attachment in base64
#     part.add_header(
#         "Content-Disposition", f'attachment; filename={file_path.split("/")[-1]}'
#     )
#     msg.attach(part)

# Connect to the SMTP server and send the email
try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    # server.set_debuglevel(1)
    server.login(username, password)  # Login to your email account
    text = msg.as_string()  # Convert the message to a string
    server.sendmail(sender_email, receiver_email, text)  # Send the email
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    server.quit()  # Close the server connection
