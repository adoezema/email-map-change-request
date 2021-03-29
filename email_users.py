import os
import logging
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List
from rich.logging import RichHandler

#TODO: Add Type Hints and Docstrings

logging.basicConfig(level="INFO", format='%(asctime)s - %(message)s',
                        datefmt='[%X]', handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger('rich')


def email_report(recipients: List, html_table: str, attachment_path: str, num_of_orgs: int):
    EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

    msg = MIMEMultipart()
    msg['Subject'] = 'Map Change Request Report'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ', '.join(recipients)

    body = f"""<html>
        <head></head>
        <body>
            <h3>This is an auto-generate email</h3>
            <p>{num_of_orgs} ArcGIS Online Accounts were scanned and processed. Below is a table of all open map change requests by community. Any 
                community not listed does not have any open map change request points.
            </p>
            {html_table}
        </body>
    </html>"""

    msg.attach(MIMEText(body, 'html'))

    with open(attachment_path, 'rb') as attachment:
        att = MIMEBase('application', 'octet-stream')
        att.set_payload(attachment.read())

    encoders.encode_base64(att)

    att.add_header('Content-Disposition', f'attachment; filename={Path(attachment_path).name}')

    msg.attach(att)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp: 

        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        log.info(f'[EMAIL] Emailing Report {",".join(recipients)}')
        smtp.sendmail(EMAIL_ADDRESS, recipients, msg.as_string())
    