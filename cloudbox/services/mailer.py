from flask_mail import Message

from cloudbox import mail, celery

class InternalServerError(Exception):
    pass
@celery.task
def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    try:
        mail.send(msg)
    except ConnectionRefusedError:
        raise InternalServerError("[MAIL SERVER] not working")

