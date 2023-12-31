from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.db import models
from django.db.models import Count


class User(AbstractBaseUser, PermissionsMixin):
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(max_length=46, unique=True)
    image = models.ImageField(upload_to='user_images', verbose_name="Аватарка", blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_private = models.BooleanField(default=False, verbose_name='Приватный ?')
    is_receive_notifications = models.BooleanField(default=True, verbose_name='Подписан на рассылку?')
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'image', 'phone_number', 'is_receive_notifications']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def get_user_s_subscribes(self):
        subs = Subscribes.objects.filter(subscriber=self)
        return [sub.author for sub in subs]

    @property
    def get_user_s_subscribers(self):
        subs = Subscribes.objects.filter(author=self)
        return [sub.subscriber for sub in subs]

    @property
    def total_subscribers(self):
        return len(self.get_user_s_subscribers)

    @property
    def total_subscribes(self):
        return len(self.get_user_s_subscribes)

    def is_user_subscribed(self, user):
        if Subscribes.objects.filter(author=self, subscriber=user):
            return True
        return False

    @staticmethod
    def most_popular_authors():
        count_subscribes = Subscribes.objects.all().values('author').order_by('-author__count').annotate(
            Count('author'))[:3]
        users = [User.objects.get(pk=subscribes['author']) for subscribes in count_subscribes]
        return users


class Subscribes(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='UsersSubscribesAuthor')
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.author} {self.subscriber}"
