from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from main.models import Themes, Cards, ThemeComments, CardComments, ThemeLikes, CardLikes
from users.models import Subscribes
from .tasks import send_email


@receiver(pre_save, sender=Themes)
def email_notify(sender, instance, **kwargs):
    if instance.id is None:
        if not instance.is_private:
            if instance.user.get_user_s_subscribers:
                subscribers = instance.user.get_user_s_subscribers
                subscribers_email = [sub.email for sub in subscribers if sub.is_receive_notifications]

                email_data = {
                    'subject': f'У {instance.user.username} новая тема! {instance.title}',
                    'recipient_list': subscribers_email,
                    'message': f'У {instance.user.username} новая тема! {instance.title}\n'
                               f'это сообщение пришло вам так как вы подписанны на {instance.user.username}\n'
                               f'если вы хотите отменить рассылку #TODO()'
                }

                send_email.delay(email_data)


@receiver(pre_save, sender=Cards)
def email_notify(sender, instance, **kwargs):
    if instance.id is None:
        if not instance.is_private:
            if instance.user.get_user_s_subscribers:
                subscribers = instance.user.get_user_s_subscribers
                subscribers_email = [sub.email for sub in subscribers if sub.is_receive_notifications]

                email_data = {
                    'subject': f'У {instance.user.username} новая карточка! {instance.title}',
                    'recipient_list': subscribers_email,
                    'message': f'У {instance.user.username} новая карточка! {instance.title}\n'
                               f'это сообщение пришло вам так как вы подписанны на {instance.user.username}\n'
                               f'если вы хотите отменить рассылку #TODO()'
                }

                send_email.delay(email_data)


@receiver(pre_save, sender=CardComments)
def email_notify(sender, instance, **kwargs):
    if instance.id is None:
        if instance.card.user.is_receive_notifications:
            if instance.sub_comment_to:
                email_data = {
                    'subject': f'Пользователь {instance.user.username} ответил на ваш коментарий {instance.sub_comment_to.content[:10]}...',
                    'recipient_list': [instance.sub_comment_to.user.email],
                    'message': f'Пользователь {instance.user.username} ответил на ваш коментарий {instance.sub_comment_to.content[:10]}... \n'
                               f'{instance.content}',
                }

            else:
                email_data = {
                    'subject': f'Пользователь {instance.user.username} оставил коментарий вашей теме {instance.card.title}...',
                    'recipient_list': [instance.card.user.email],
                    'message': f'Пользователь {instance.user.username} оставил коментарий вашей карточке {instance.card.title}... \n'
                               f'{instance.content}',
                }
            send_email.delay(email_data)


@receiver(pre_save, sender=ThemeComments)
def email_notify(sender, instance, **kwargs):
    if instance.id is None:
        if instance.theme.user.is_receive_notifications:
            if instance.sub_comment_to:
                email_data = {
                    'subject': f'Пользователь {instance.user.username} ответил на ваш коментарий {instance.sub_comment_to.content[:10]}...',
                    'recipient_list': [instance.sub_comment_to.user.email],
                    'message': f'Пользователь {instance.user.username} ответил на ваш коментарий {instance.sub_comment_to.content[:10]}... \n'
                               f'{instance.content}',
                }

            else:
                email_data = {
                    'subject': f'Пользователь {instance.user.username} оставил коментарий вашей теме {instance.theme.title}...',
                    'recipient_list': [instance.theme.user.email],
                    'message': f'Пользователь {instance.user.username} оставил коментарий вашей карточке {instance.theme.title}... \n'
                               f'{instance.content}',
                }

            send_email.delay(email_data)


@receiver(post_save, sender=ThemeLikes)
def email_notify(sender, instance, **kwargs):

    if instance.user.is_receive_notifications:
        email_data = {

            'subject': f"ваша тема {instance.theme.title} понравилась {instance.user.username}",
            'recipient_list': [instance.theme.user.email],
            'message': f"ваша тема {instance.theme.title} понравилась {instance.user.username}",

        }
        send_email.delay(email_data)


@receiver(post_save, sender=CardLikes)
def email_notify(sender, instance, **kwargs):
    if instance.user.is_receive_notifications:
        email_data = {

            'subject': f"ваша карточка {instance.card.title} понравилась {instance.user.username}",
            'recipient_list': [instance.card.user.email],
            'message': f"ваша карточка {instance.card.title} понравилась {instance.user.username}",

        }
        send_email.delay(email_data)


@receiver(post_save, sender=Subscribes)
def email_notify(sender, instance, **kwargs):
    if instance.author.is_receive_notifications:
        email_data = {

            'subject': f'Пользователь {instance.subscriber.username} подписался на ваши обновления...',
            'recipient_list': [instance.author.email],
            'message': f'Пользователь {instance.subscriber.username} подписался на ваши обновления...',

        }

        send_email.delay(email_data)