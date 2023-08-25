from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models
from django.db.models import Count, Sum
from users.models import User


class ThemeViews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class CardViews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class ThemeLikes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class CardLikes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class CardComments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    time_created = models.TimeField(auto_now_add=True)
    sub_comment_to = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, )


class Cards(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Автор")
    is_private = models.BooleanField(default=False)
    title = models.CharField(max_length=255, verbose_name="Название")
    content = models.TextField(verbose_name="Контент")

    search_vector = SearchVectorField(null=True)

    comments = models.ManyToManyField(CardComments)
    likes = models.ManyToManyField(CardLikes)
    views = models.ManyToManyField(CardViews)

    class Meta:
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"
        indexes = [GinIndex(fields=["search_vector"])]

    def __str__(self):
        return f"{self.title}"

    def update_search_vector(self, *args):
        qs = Cards.objects.filter(pk=self.pk)
        qs.update(search_vector=SearchVector(*args))

    @staticmethod
    def get_super_cards_by_user(user):
        return Cards.objects.filter(user=user, themes__isnull=True)
        # TODO()

    @property
    def users_with_access(self):
        lst_users_with_access = []
        for row in CardAccess.objects.filter(card=self).values('user'):
            lst_users_with_access.append(User.objects.get(pk=row['user']))
        return lst_users_with_access

    @classmethod
    def count_user_s_likes_received(cls, user):
        return Cards.objects.filter(user=user)\
            .prefetch_related('likes')\
            .annotate(count_likes=Count('likes'))\
            .aggregate(sum_count_likes=Sum('count_likes')).get('sum_count_likes', 0)

    @classmethod
    def count_user_s_views_received(cls, user):
        return Cards.objects.filter(user=user)\
            .prefetch_related('views')\
            .annotate(count_views=Count('views'))\
            .aggregate(sum_count_views=Sum('count_views')).get('sum_count_views', 0)

    @classmethod
    def count_user_s_comment_received(cls, user):
        return Cards.objects.filter(user=user) \
            .prefetch_related('comments') \
            .annotate(count_comments=Count('comments')) \
            .aggregate(sum_count_comments=Sum('count_comments')).get('sum_count_comments', 0)

    @staticmethod
    def most_popular_cards():
        return Cards.objects.annotate(
            count_likes=Count('likes'), count_comments=Count('comments'), count_views=Count('views')
        ).order_by('likes', 'comments', 'views')[:3]


class ThemeComments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    time_created = models.TimeField(auto_now_add=True)
    sub_comment_to = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, )


class Themes(models.Model):
    is_private = models.BooleanField(default=False)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Автор")
    title = models.CharField(max_length=255, verbose_name="Название")
    parent_theme = models.ForeignKey(to="self", on_delete=models.CASCADE, blank=True, null=True,
                                     verbose_name="Подтема для")

    search_vector = SearchVectorField(null=True)

    comments = models.ManyToManyField(ThemeComments, related_name='comments')
    likes = models.ManyToManyField(ThemeLikes)
    views = models.ManyToManyField(ThemeViews)
    sub_themes = models.ManyToManyField('self')
    sub_cards = models.ManyToManyField(Cards)

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"
        indexes = [GinIndex(fields=["search_vector"])]

    def __str__(self):
        return f"{self.title}"

    def update_search_vector(self, *args):
        # TODO(update_serch vectore)
        qs = Themes.objects.filter(pk=self.pk)
        qs.update(search_vector=SearchVector(*args))

    @staticmethod
    def get_super_themes_by_user(user):
        # TODO()
        return Themes.objects.filter(user=user)

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

    @classmethod
    def count_user_s_likes_received(cls, user):
        return Themes.objects.filter(user=user)\
            .prefetch_related('likes')\
            .annotate(count_likes=Count('likes'))\
            .aggregate(sum_count_likes=Sum('count_likes')).get('sum_count_likes', 0)

    @classmethod
    def count_user_s_views_received(cls, user):
        return Themes.objects.filter(user=user)\
            .prefetch_related('views')\
            .annotate(count_views=Count('views'))\
            .aggregate(sum_count_views=Sum('count_views')).get('sum_count_views', 0)

    @classmethod
    def count_user_s_comment_received(cls, user):
        return Themes.objects.filter(user=user) \
            .prefetch_related('comments') \
            .annotate(count_comments=Count('comments')) \
            .aggregate(sum_count_comments=Sum('count_comments')).get('sum_count_comments', 0)

    @staticmethod
    def most_popular_theme():
        return Themes.objects.annotate(
            count_likes=Count('likes'), count_comments=Count('comments'), count_views=Count('views')
        ).order_by('likes', 'comments', 'views')[:3]


class CardAccess(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    card = models.ForeignKey(to=Cards, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Доступ к карточке'
        verbose_name_plural = 'Доступ к карточкам'

    def __str__(self):
        return f"{self.user} -> {self.card}"


class ThemeAccess(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    theme = models.ForeignKey(to=Themes, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Доступ к теме'
        verbose_name_plural = 'Доступ к темам'

    def __str__(self):
        return f"{self.user} -> {self.theme}"

