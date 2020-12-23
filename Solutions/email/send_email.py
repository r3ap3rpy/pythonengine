### https://myaccount.google.com/security?rapt=AEjHL4Mtr12tMpPNt-PdSWfaBNlRrPUyaqYJHLvaKr5ZSSWQGXEDAlcXDFNVuqdP_82y7tl4k18DGtODoIXdgomCwTcG5m_GqQ
### Add a new application password!

import smtplib, ssl, os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

worker = (os.getenv('COMPUTERNAME') if os.name == 'nt' else os.getenv('HOSTNAME'))

receiver_email = "r3ap3rpy@gmail.com"

port = 587
smtp_server = "smtp.gmail.com"
sender_email = os.getenv('GMAIL_USER')
password = os.getenv('GMAIL_PASS')

msg = MIMEMultipart('mixed')
msg['Subject'] = f"PyEngine :: {worker} :: E-Mail message"
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Cc'] = sender_email

HTML = "<html>"
HTML += f"<h4>Dear Recipient,</h4>"
HTML += "Below are the details of your request!"
HTML += "<hr>"
HTML += "<p>Best Regards,<br>PythonEngine</p>"
HTML += "</html>"
Final = MIMEText(HTML, 'html')
msg.attach(Final)

context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())