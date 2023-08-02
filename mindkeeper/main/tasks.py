from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_notification(email_data):
    print('task')
    send_mail(
        subject=email_data['subject'],
        recipient_list=email_data['recipient_list'],
        from_email=settings.EMAIL_HOST_USER,
        message=email_data['message'],
    )
