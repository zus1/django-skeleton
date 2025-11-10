import logging
import os

from django.conf import settings
from django.core.mail import send_mail
from sendgrid import SendGridAPIClient, Mail

class Mailer:
    def __init__(self):
        self.__sandbox = settings.EMAIL_SANDBOX
        self.__from = settings.EMAIL_FROM_ADDRESS
        self.__from_no_reply = settings.EMAIL_NO_REPLY_ADDRESS
        self.__reply = True

    def send(self, subject: str, to: str, html: str = None, text: str = None, reply: bool = True)->bool:
        self.__reply = reply

        # Sandbox uses MailCatcher
        if self.__sandbox:
            text = text if text else None
            message = text if not html else None

            try:
                sent = send_mail(
                    subject=subject,
                    message=message,
                    from_email=self.__from if self.__reply else self.__from_no_reply,
                    recipient_list=[to],
                    fail_silently=False,
                    html_message=html if html else None,
                )
            except Exception as e:
                logging.getLogger('email').error('Could not send email. Error occurred: %s' % str(e))
                raise e
            return sent > 0

        return self.__send_live(to=to, subject=subject, html=html, text=text)

    #If not using Sendgrid, replace with desired email client
    def __send_live(self, to: str, subject: str, html: str = None, text: str = None)->bool:
        email = Mail(
            from_email=self.__from if self.__reply else self.__from_no_reply,
            to_emails=[to],
            subject=subject,
            html_content=html if html else None,
            plain_text_content=text if text else None,
        )
        sg = SendGridAPIClient(os.environ.get('SENDGRID_KEY'))
        response = sg.send(email)

        if response.status_code != 200:
            logging.getLogger('email').error('Could not send email. Error occurred: %s' % str(response.body))

            return False

        return True