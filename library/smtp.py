import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from data import config



settings = config.getConfig()

def sendEmail(html, receiver_email, subject):
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = settings.sender_email
    message["To"] = receiver_email
    message.attach(MIMEText(html, "html"))
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(settings.smtp_server, settings.smtp_port, context=context) as server:
        server.login(settings.sender_email, settings.smtp_password)
        server.sendmail(settings.sender_email, receiver_email, message.as_string())

def sendErrorEmail(e):
    html = """\
<html>
  <body>
    <p>Error with strava hill checker</p>
    <p>""" + str(e) + """</p>
  </body>
</html>
"""
    message = MIMEMultipart()
    message["Subject"] = 'Strava hill checker Error'
    message["From"] = settings.sender_email
    message["To"] = settings.error_email
    message.attach(MIMEText(html, "html"))
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(settings.smtp_server, settings.smtp_port, context=context) as server:
        server.login(settings.sender_email, settings.smtp_password)
        server.sendmail(settings.sender_email, settings.errorEmail, message.as_string())
