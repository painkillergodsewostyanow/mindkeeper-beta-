from django.db import models
from PIL import Image
from users.models import User
from django_cleanup import cleanup


class CountableMixin:
    @classmethod
    def count_received(cls, countable, user):
        if issubclass(cls, Themes):
            return CountStrategy.count_received_theme(Themes, countable, user)
        if issubclass(cls, Cards):
            return CountStrategy.count_received_card(Cards, countable, user)

    @staticmethod
    def count_placed(countable, user):
        return countable.objects.filter(user=user).count()


class CountStrategy:
    @staticmethod
    def count_received_theme(a, countable, user):
        total = 0
        for obj in a.objects.filter(user=user):
            total += countable.objects.filter(theme=obj).count()

        return total

    @staticmethod
    def count_received_card(a, countable, user):
        total = 0
        for obj in a.objects.filter(user=user):
            total += countable.objects.filter(card=obj).count()

        return total


@cleanup.select
class Themes(models.Model, CountableMixin):
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

    @property
    def users_with_access(self):
        lst_users_with_access = []
        for row in ThemeAccess.objects.filter(theme=self).values('user'):
            lst_users_with_access.append(User.objects.get(pk=row['user']))
        return lst_users_with_access

    @property
    def get_sub_themes(self):
        return Themes.objects.filter(sub_theme_to=self)

    @property
    def get_cards(self):
        return Cards.objects.filter(theme=self)

    @property
    def views(self):
        return ThemeViews.objects.filter(theme=self).count()

    @property
    def likes(self):
        return ThemeLikes.objects.filter(theme=self).count()

    @property
    def comments(self):
        return ThemeComments.objects.filter(theme=self)

    @classmethod
    def count_user_s_likes_received(cls, user):
        return cls.count_received(ThemeLikes, user)

    @classmethod
    def count_user_s_views_received(cls, user):
        return cls.count_received(ThemeViews, user)

    @classmethod
    def count_user_s_comment_received(cls, user):
        return cls.count_received(ThemeComments, user)

    @classmethod
    def count_user_s_likes_placed(cls, user):
        return cls.count_placed(ThemeLikes, user)

    @classmethod
    def count_user_s_views_placed(cls, user):
        return cls.count_placed(ThemeViews, user)

    @classmethod
    def count_user_s_comment_placed(cls, user):
        return cls.count_placed(ThemeComments, user)


@cleanup.select
class Cards(models.Model, CountableMixin):
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

    @property
    def comments(self):
        return CardComments.objects.filter(card=self)

    @classmethod
    def count_user_s_likes_received(cls, user):
        return cls.count_received(CardLikes, user)

    @classmethod
    def count_user_s_views_received(cls, user):
        return cls.count_received(CardViews, user)

    @classmethod
    def count_user_s_comment_received(cls, user):
        return cls.count_received(CardComments, user)

    @classmethod
    def count_user_s_likes_placed(cls, user):
        return cls.count_placed(CardLikes, user)

    @classmethod
    def count_user_s_views_placed(cls, user):
        return cls.count_placed(CardViews, user)

    @classmethod
    def count_user_s_comment_placed(cls, user):
        return cls.count_placed(CardComments, user)


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


class ThemeComments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    theme = models.ForeignKey(Themes, on_delete=models.CASCADE)
    content = models.TextField()
    sub_comment_to = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True,)

    def get_sub_comment(self):
        return ThemeComments.objects.filter(sub_comment_to=self)


class CardComments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(Cards, on_delete=models.CASCADE)
    content = models.TextField()
    sub_comment_to = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True,)

    def get_sub_comment(self):
        return CardComments.objects.filter(sub_comment_to=self)
