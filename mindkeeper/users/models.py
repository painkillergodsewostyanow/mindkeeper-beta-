from django.contrib.auth.models import AbstractBaseUser, UserManager, AbstractUser
from django.db import models
from main.mixins import ResizeImageOnSaveMixin, CompressImageOnSaveMixin


class User(AbstractUser):
    # is_active = models.BooleanField(default=False)
    # is_staff = models.BooleanField(default=False)
    # is_superuser = models.BooleanField(default=False)
    # username = models.CharField(max_length=26, unique=True)
    image = models.ImageField(upload_to='user_images', verbose_name="Аватарка", blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_private = models.BooleanField(default=False, verbose_name='Приватный ?')
    is_email_verified = models.BooleanField(default=False, verbose_name='Почта подтверденна?')
    is_receive_notifications = models.BooleanField(default=True, verbose_name='Подписан на рассылку?')

    # USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ('email',)
    #
    # objects = UserManager()

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
