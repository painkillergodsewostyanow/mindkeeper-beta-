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

    @property
    def get_super_themes(self):
        return Themes.objects.filter(user=self, sub_theme_to__isnull=True)


class Themes(models.Model):
    # TODO(image)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Автор")
    title = models.CharField(max_length=255, verbose_name="Название")
    sub_theme_to = models.ForeignKey(to="self", on_delete=models.CASCADE, blank=True, null=True, verbose_name="Подтема для")

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"


class Cards(models.Model):
    # TODO(image)
    theme = models.ForeignKey(to=Themes, on_delete=models.CASCADE, verbose_name="Тема")
    title = models.CharField(max_length=255, verbose_name="Название")
    content = models.TextField(verbose_name="Контент")

    def __str__(self):
        return f"{self.theme}, {self.title}"

    class Meta:
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"
