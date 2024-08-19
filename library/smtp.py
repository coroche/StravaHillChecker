import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from data import config
from dataclasses import dataclass
from typing import List

@dataclass
class Email:
	html: str
	address: str
	subject: str


settings = config.getConfig()

def sendEmails(emails: List[Email]) -> None:
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL(settings.smtp_server, settings.smtp_port, context=context) as server:
		server.login(settings.sender_email, settings.smtp_password)
		
		for email in emails:
			message = MIMEMultipart()
			message["Subject"] = email.subject
			message["From"] = settings.sender_email
			message["To"] = email.address
			message.attach(MIMEText(email.html, "html"))
			server.sendmail(settings.sender_email, email.address, message.as_string())

def sendErrorEmail(e: Exception) -> None:
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
