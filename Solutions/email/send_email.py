### https://myaccount.google.com/security?rapt=AEjHL4Mtr12tMpPNt-PdSWfaBNlRrPUyaqYJHLvaKr5ZSSWQGXEDAlcXDFNVuqdP_82y7tl4k18DGtODoIXdgomCwTcG5m_GqQ
### Add a new application password!
import ssl, smtplib, os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart




worker = (os.getenv('COMPUTERNAME') if os.name == 'nt' else os.getenv('HOSTNAME'))

reciever_email = "r3ap3rpy@gmail.com"

port = 587
smtp_server = 'smtp.gmail.com'
sender_email = os.getenv('GMAIL_USER')
password = os.getenv('GMAIL_PASS')

msg = MIMEMultipart('mixed')
msg['Subject'] = f"PyEngine :: {worker} :: Email message"
msg['From'] = sender_email
msg['To'] = reciever_email

HTML = "<html>"
HTML += "<h4> Dear Recipient,</h4>"
HTML += "<p>Below are the results</p>"
HTML += "<p>Best Regards,<br>PyEngine</p>"
HTML += "</html>"

FinalMessage = MIMEText(HTML,'html')
msg.attach(FinalMessage)

with smtplib.SMTP(smtp_server,port) as server:
        server.ehlo()
        server.starttls(context = ssl.create_default_context())
        server.ehlo()
        server.login(sender_email,password)
        server.sendmail(sender_email,reciever_email,msg.as_string())