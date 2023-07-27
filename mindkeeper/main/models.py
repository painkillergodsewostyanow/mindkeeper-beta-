from django.db import models
from PIL import Image
from users.models import User
from django_cleanup import cleanup


class ResizeOnSaveMixin:
    max_height = 800
    max_weight = 600
    resize_fields = () # TODO()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            image = Image.open(self.image.path)
            if image.height > self.max_height or image.width > self.max_weight:
                image.thumbnail((self.max_height, self.max_weight))
                image.save(self.image.path)


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
            total += countable.objects.filter(obj=obj).count()

        return total

    @staticmethod
    def count_received_card(a, countable, user):
        total = 0
        for obj in a.objects.filter(user=user):
            total += countable.objects.filter(obj=obj).count()

        return total


@cleanup.select
class Themes(ResizeOnSaveMixin, CountableMixin, models.Model):
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
        return ThemeViews.objects.filter(obj=self).count()

    @property
    def likes(self):
        return ThemeLikes.objects.filter(obj=self).count()

    @property
    def comments(self):
        return ThemeComments.objects.filter(obj=self)

    @property
    def count_comments(self):
        return self.comments.count()

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
class Cards(ResizeOnSaveMixin, CountableMixin, models.Model):
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
        return CardViews.objects.filter(obj =self).count()

    @property
    def likes(self):
        return CardLikes.objects.filter(obj=self).count()

    @property
    def comments(self):
        return CardComments.objects.filter(obj=self)

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
    obj = models.ForeignKey(Themes, on_delete=models.CASCADE)


class CardViews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    obj = models.ForeignKey(Cards, on_delete=models.CASCADE)


class ThemeLikes(models.Model):
    obj = models.ForeignKey(Themes, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class CardLikes(models.Model):
    obj = models.ForeignKey(Cards, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    time_created = models.TimeField(auto_now_add=True)
    sub_comment_to = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True,)


class ThemeComments(Comments):
    obj = models.ForeignKey(Themes, on_delete=models.CASCADE)

    @property
    def get_sub_comments(self):
        return ThemeComments.objects.filter(sub_comment_to=self)


class CardComments(Comments):
    obj = models.ForeignKey(Cards, on_delete=models.CASCADE)

    @property
    def get_sub_comments(self):
        return CardComments.objects.filter(sub_comment_to=self)


# class Notifications(models.Model):
#     subscriber = models.ForeignKey(User, on_delete=models.CASCADE)
#     is_checked = models.BooleanField(default=False)
#
#
# class CardNotifications(Notifications):
#     obj = models.ForeignKey(Cards, on_delete=models.CASCADE)
