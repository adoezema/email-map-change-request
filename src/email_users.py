import os
import smtplib


EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

if __name__ =="__main__":
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo() 

        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
        subject = 'PYTHON TEST EMAIL'
        body = 'This is a test emial.'

        msg = f'Subject: {subject}\n\n{body}'

        smtp.sendmail(EMAIL_ADDRESS, 'TEST@EMAIL.COM', msg)
    