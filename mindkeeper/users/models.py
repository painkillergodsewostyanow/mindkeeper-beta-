from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    image = models.ImageField(upload_to='user_images', verbose_name="Аватарка", blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    if_private = models.BooleanField(default=False, verbose_name='Приватный ?')
    is_email_verified = models.BooleanField(default=False, verbose_name='Почта подтверденна?')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def get_user_s_subscribes(self):
        return Subscribes.objects.filter(subscriber=self)

    @property
    def get_user_s_subscribers(self):
        return Subscribes.objects.filter(author=self)

    def is_user_subscribed(self, user):
        if Subscribes.objects.filter(author=self, subscriber=user):
            return True
        return False


class Subscribes(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='UsersSubscribesAuthor')
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE)