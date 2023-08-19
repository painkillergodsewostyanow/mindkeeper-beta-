from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .tasks import send_verify_email
from .models import User