# EMAIL SERVICE
# This module provides functionality to send emails using the SMTP protocol.

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from extensions import db
from models.user import User


def account_activation_email(email, activation_token, name):
    """Send account activation email to the user."""
    subject = "Activate Your Account"
    sender_email = current_app.config['MAIL_USERNAME']
    receiver_email = email
    activation_link = f"{current_app.config['FRONTEND_URL']}/activate/{activation_token}"

    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    body = f"""
    Hi {name},

    Please click the link below to activate your account:
    {activation_link}

    Thank you!
    """
    
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(sender_email, current_app.config['MAIL_PASSWORD'])
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False