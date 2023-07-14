from django.db import models
from PIL import Image
from users.models import User


class Themes(models.Model):
    image = models.ImageField(upload_to="themes_image", blank=True)
    is_private = models.BooleanField(default=False)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Автор")
    title = models.CharField(max_length=255, verbose_name="Название")
    sub_theme_to = models.ForeignKey(to="self", on_delete=models.CASCADE, blank=True, null=True, verbose_name="Подтема для")

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            image = Image.open(self.image.path)
            if image.height > 800 or image.width> 600:
                image.thumbnail((800, 600))
                image.save(self.image.path)

    @staticmethod
    def get_super_themes_by_user(user):
        return Themes.objects.filter(user=user, sub_theme_to__isnull=True)

    def users_with_access(self):
        lst_users_with_access = []
        for row in ThemeAccess.objects.filter(theme=self).values('user'):
            lst_users_with_access.append(User.objects.get(pk=row['user']))
        return lst_users_with_access

    def get_sub_themes(self):
        return Themes.objects.filter(sub_theme_to=self)

    def get_cards(self):
        return Cards.objects.filter(theme=self)

    @property
    def views(self):
        return ThemeViews.objects.filter(theme=self).count()

    @property
    def likes(self):
        return ThemeLikes.objects.filter(theme=self).count()


class Cards(models.Model):
    # TODO(Возможность выдавать доступ определенным людям)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Автор")
    image = models.ImageField(upload_to="card_image", blank=True)
    is_private = models.BooleanField(default=False)
    theme = models.ForeignKey(to=Themes, on_delete=models.CASCADE, verbose_name="Тема",
                              blank=True, null=True,
                              )
    title = models.CharField(max_length=255, verbose_name="Название")
    content = models.TextField(verbose_name="Контент")

    class Meta:
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"

    def __str__(self):
        return f"{self.theme}, {self.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            image = Image.open(self.image.path)
            if image.height > 800 or image.width> 600:
                image.thumbnail((800, 600))
                image.save(self.image.path)

    @staticmethod
    def get_super_cards_by_user(user):
        return Cards.objects.filter(user=user, theme__isnull=True)

    @property
    def users_with_access(self):
        lst_users_with_access = []
        for row in CardAccess.objects.filter(card=self).values('user'):
            lst_users_with_access.append(User.objects.get(pk=row['user']))
        return lst_users_with_access

    @property
    def views(self):
        return CardViews.objects.filter(card=self).count()

    @property
    def likes(self):
        return CardLikes.objects.filter(card=self).count()


class CardAccess(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    card = models.ForeignKey(to=Cards, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Доступ к карточке'
        verbose_name_plural = 'Доступ к карточкам'

    def __str__(self):
        return f"{self.user}->{self.card}"


class ThemeAccess(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    theme = models.ForeignKey(to=Themes, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Доступ к теме'
        verbose_name_plural = 'Доступ к темам'

    def __str__(self):
        return f"{self.user}->{self.theme}"


class ThemeViews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    theme = models.ForeignKey(Themes, on_delete=models.CASCADE)


class CardViews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(Cards, on_delete=models.CASCADE)


class ThemeLikes(models.Model):
    theme = models.ForeignKey(Themes, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class CardLikes(models.Model):
    card = models.ForeignKey(Cards, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class ThemeComment(models.Model):
    theme = models.ForeignKey(Themes, on_delete=models.CASCADE)
    content = models.TextField()
    sub_comment_to = models.ForeignKey('self', on_delete=models.CASCADE)


class CardComment(models.Model):
    card = models.ForeignKey(Cards, on_delete=models.CASCADE)
    content = models.TextField()
    sub_comment_to = models.ForeignKey('self', on_delete=models.CASCADE)
