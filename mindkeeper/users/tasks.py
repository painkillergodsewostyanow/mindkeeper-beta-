from celery import shared_task
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .models import User


@shared_task
def send_verify_email(user_pk):
    user = User.objects.get()

    context = {
        'domain': settings.DOMAIN_NAME,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    }

    subject = "Для завершения регистрации подтвердите почту"
    message = render_to_string(
        'users/registration/verify_mail.html', context
    )
    send_mail(
        subject=subject,
        message=message,
        recipient_list=[user.email],
        from_email=settings.EMAIL_HOST_USER,
    )
