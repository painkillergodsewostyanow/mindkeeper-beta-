from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    image = models.ImageField(upload_to='user_images', verbose_name="Аватарка", blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    if_private = models.BooleanField(default=False, verbose_name='Приватный ?')
    is_email_verified = models.BooleanField(default=False, verbose_name='Почта подтверденна?')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


