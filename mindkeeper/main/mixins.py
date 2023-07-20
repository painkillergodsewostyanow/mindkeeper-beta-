from main.models import Themes, Cards


class CountableMixin:
    @staticmethod
    def count_received(a, countable, user):
        if isinstance(a, Themes):
            CountStrategy.count_received_theme(Themes, countable, user)
        if isinstance(a, Cards):
            CountStrategy.count_received_card(Cards, countable, user)

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

    @classmethod
    def count_received_card(cls, countable, user):
        total = 0
        for obj in cls.objects.filter(user=user):
            total += countable.objects.filter(card=obj).count()

        return total