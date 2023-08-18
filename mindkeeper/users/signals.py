from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .tasks import send_verify_email
from .models import User


@receiver(post_save, sender=User)
def send_verify_email_on_user_create(instance, **kwargs):
    send_verify_email.delay(instance.pk)


@receiver(pre_save, sender=User)
def logout_if_email_changed(instance, **kwargs):
    ...