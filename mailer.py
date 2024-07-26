import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email(report_content, attachment_file=None):
    recipient_email='aniksinghal2104@gmail.com'
    filename = os.path.basename(attachment_file)
    sender_email = 'sendermail'
    app_password = 'sender password'
    subject="Pneumonia Report"
    # Connect to SMTP server
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(sender_email, app_password)

        # Construct the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(report_content, 'html'))  # Assuming HTML content

        # Add attachment (if provided)
    if attachment_file:
        with open(attachment_file, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(f'Content-Disposition', f'attachment; filename={filename}')
            msg.attach(part)
            # ... Code to create and attach the image as MIME part ...

        # Send the email
    print("\nsending email\n")
    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()

    print('Email sent successfully!')
