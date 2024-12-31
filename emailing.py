# Tutorial Here : https://www.youtube.com/watch?v=vCTP-Ykn_kw

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from credentials import email, password


with open("testEmailTemplate.html", mode='r') as html:
    html_content = html.read()


msg = MIMEMultipart()
msg['From'] = email
msg['To'] = "taran.s.lau@gmail.com"
msg['Subject'] = "Python Test Email"

html_mail = MIMEText(html_content, 'html')
msg.attach(html_mail)

obj = smtplib.SMTP("smtp.gmail.com", 587)
obj.starttls()
obj.login(email, password)

# Non html email example
# from_addr = email
# recipients = ["keenanlau12@gmail.com", "taran.s.lau@gmail.com"]
# obj.sendmail(from_addr=from_addr, to_addrs=recipients, msg="Hi this is a test email from python!")
# obj.quit()

text = msg.as_string()
obj.sendmail(email, ["taran.s.lau@gmail.com"], text)
obj.quit()

