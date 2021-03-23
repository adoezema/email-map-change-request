import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

to_users = ['TEST_EMAIL@emial.com']

msg = MIMEMultipart()
msg['Subject'] = 'Map Change Request Report'
msg['From'] = EMAIL_ADDRESS
msg['To'] = ', '.join(to_users)

body = '<h1>Test</h1>'

msg.attach(MIMEText(body, 'html'))

if __name__ =="__main__":
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp: 

        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
        smtp.sendmail(EMAIL_ADDRESS, to_users, msg.as_string())
    