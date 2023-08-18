from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models
from django.db.models import Count
from random import shuffle as shake
from users.models import User
from django_cleanup import cleanup
from .mixins import ResizeImageOnSaveMixin, CompressImageOnSaveMixin


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
class Themes(CompressImageOnSaveMixin, ResizeImageOnSaveMixin, CountableMixin, models.Model):
    quality = 40
    image = models.ImageField(upload_to="themes_image", blank=True)
    is_private = models.BooleanField(default=False)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Автор")
    title = models.CharField(max_length=255, verbose_name="Название")
    parent_theme = models.ForeignKey(to="self", on_delete=models.CASCADE, blank=True, null=True,
                                     verbose_name="Подтема для")

    search_vector = SearchVectorField(null=True)

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"
        indexes = [GinIndex(fields=["search_vector"])]

    def __str__(self):
        return f"{self.title}"

    def update_search_vector(self, *args):
        qs = Themes.objects.filter(pk=self.pk)
        qs.update(search_vector=SearchVector(*args))

    @staticmethod
    def get_super_themes_by_user(user):
        return Themes.objects.filter(user=user, parent_theme__isnull=True)

    @property
    def users_with_access(self):
        lst_users_with_access = []
        for row in ThemeAccess.objects.filter(theme=self).values('user'):
            lst_users_with_access.append(User.objects.get(pk=row['user']))
        return lst_users_with_access

    @property
    def get_sub_themes(self):
        return Themes.objects.filter(parent_theme=self)

    @property
    def get_cards(self):
        return Cards.objects.filter(parent_theme=self)

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

    @staticmethod
    def most_popular_theme():
        themes = []
        most_popular_by_views = ThemeViews.objects.all().values('obj').order_by('-obj__count').annotate(Count('obj'))[:3]
        most_popular_by_likes = ThemeLikes.objects.all().values('obj').order_by('-obj__count').annotate(Count('obj'))[:3]
        most_popular_by_comments = ThemeComments.objects.all().values('obj').order_by('-obj__count').annotate(Count('obj'))[:3]
        themes += [query['obj'] for query in most_popular_by_views]
        themes += [query['obj'] for query in most_popular_by_likes]
        themes += [query['obj'] for query in most_popular_by_comments]
        shake(themes)

        return [Themes.objects.get(pk=theme) for theme in set(themes)][:3]


@cleanup.select
class Cards(CompressImageOnSaveMixin, ResizeImageOnSaveMixin, CountableMixin, models.Model):
    quality = 40
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Автор")
    image = models.ImageField(upload_to="card_image", blank=True)
    is_private = models.BooleanField(default=False)
    parent_theme = models.ForeignKey(to=Themes, on_delete=models.CASCADE, verbose_name="Тема",
                                     blank=True, null=True,
                                     )
    title = models.CharField(max_length=255, verbose_name="Название")
    content = models.TextField(verbose_name="Контент")

    search_vector = SearchVectorField(null=True)

    class Meta:
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"
        indexes = [GinIndex(fields=["search_vector"])]

    def __str__(self):
        return f"{self.parent_theme}, {self.title}"

    def update_search_vector(self, *args):
        qs = Cards.objects.filter(pk=self.pk)
        qs.update(search_vector=SearchVector(*args))

    @staticmethod
    def get_super_cards_by_user(user):
        return Cards.objects.filter(user=user, parent_theme__isnull=True)

    @property
    def users_with_access(self):
        lst_users_with_access = []
        for row in CardAccess.objects.filter(card=self).values('user'):
            lst_users_with_access.append(User.objects.get(pk=row['user']))
        return lst_users_with_access

    @property
    def views(self):
        return CardViews.objects.filter(obj=self).count()

    @property
    def likes(self):
        return CardLikes.objects.filter(obj=self).count()

    @property
    def comments(self):
        return CardComments.objects.filter(obj=self)

    @property
    def count_comments(self):
        return self.comments.count()

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

    @staticmethod
    def most_popular_cards():
        cards = []
        most_popular_by_views = CardViews.objects.all().values('obj').order_by('-obj__count').annotate(Count('obj'))[:3]
        most_popular_by_likes = CardLikes.objects.all().values('obj').order_by('-obj__count').annotate(Count('obj'))[:3]
        most_popular_by_comments = CardComments.objects.all().values('obj').order_by('-obj__count').annotate(
            Count('obj'))[:3]
        cards += [query['obj'] for query in most_popular_by_views]
        cards += [query['obj'] for query in most_popular_by_likes]
        cards += [query['obj'] for query in most_popular_by_comments]
        shake(cards)

        return [Cards.objects.get(pk=card) for card in set(cards)][:3]


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
    sub_comment_to = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, )


class ThemeComments(Comments):
    obj = models.ForeignKey(Themes, on_delete=models.CASCADE)


class CardComments(Comments):
    obj = models.ForeignKey(Cards, on_delete=models.CASCADE)

