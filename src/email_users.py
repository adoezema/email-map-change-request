import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from rich.logging import RichHandler

logging.basicConfig(level="INFO", format='%(asctime)s - %(message)s',
                        datefmt='[%X]', handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger('rich')


def email_report(recipients: List, html_table: str):
    EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

    msg = MIMEMultipart()
    msg['Subject'] = 'Map Change Request Report'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ', '.join(recipients)

    body = f"""<html>
        <head></head>
        <body>
            {html_table}
        </body>
    </html>"""

    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp: 

        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        log.info(f'[EMAIL] Emailing Report {",".join(recipients)}')
        smtp.sendmail(EMAIL_ADDRESS, recipients, msg.as_string())
    