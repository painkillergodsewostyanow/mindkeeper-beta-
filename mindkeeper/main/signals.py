import os

from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save

from mindkeeper.settings import MEDIA_ROOT, MEDIA_URL
from users.models import User
from .models import Cards, Themes, CardComments, ThemeComments
from .tasks import send_notification


@receiver(post_delete, sender=Cards)
def on_delete(sender, **kwargs):
    images = []
    html_str = kwargs['instance'].content

    # parse <img> tags from the content_html
    while "img" in html_str:
        left_enter = html_str.find('<img')
        html_str = html_str[left_enter:]
        right_enter = html_str.find('>') + 1
        images.append(html_str[:right_enter])
        html_str = html_str[right_enter:]

    # iterate <img> tags, get href and delete
    for image in images:
        left_enter = image.find(MEDIA_URL)
        image = image[left_enter + len(MEDIA_URL):]
        right_enter = image.find('"')
        path = os.path.join(MEDIA_ROOT / image[:right_enter])
        os.remove(os.path.join(path))


@receiver(post_save, sender=Themes)
def post_save_themes(sender, instance, created, update_fields, **kwargs):
    instance.update_search_vector('title')

    if not instance.is_private:
        if instance.user.get_user_s_subscribers:
            subscribers = instance.user.get_user_s_subscribers
            subscribers_email = [sub.email for sub in subscribers if
                                 sub.is_receive_notifications]

            email_data = {
                'subject': f'У {instance.user.username} новая тема! {instance.title}',
                'recipient_list': subscribers_email,
                'message': f'У {instance.user.username} новая тема! {instance.title}\n'
                           f'это сообщение пришло вам так как вы подписанны на {instance.user.username}\n'
                           f'если вы хотите отменить рассылку #TODO()'
            }

            send_notification.delay(email_data)


@receiver(post_save, sender=Cards)
def post_save_card(sender, instance, created, update_fields, **kwargs):
    instance.update_search_vector('title', 'content')

    if not instance.is_private:
        if instance.user.get_user_s_subscribers:
            subscribers = instance.user.get_user_s_subscribers
            subscribers_email = [sub.email for sub in subscribers if
                                 sub.is_receive_notifications]

            email_data = {
                'subject': f'У {instance.user.username} новая карточка! {instance.title}',
                'recipient_list': subscribers_email,
                'message': f'У {instance.user.username} новая карточка! {instance.title}\n'
                           f'это сообщение пришло вам так как вы подписанны на {instance.user.username}\n'
                           f'если вы хотите отменить рассылку #TODO()'
            }

            send_notification.delay(email_data)


@receiver(post_save, sender=CardComments)
def notify(sender, instance, **kwargs):
    if instance.card.user.is_receive_notifications:

        email_data = {
            'subject': f'Пользователь {instance.user.username} оставил коментарий вашей теме {instance.card.title}...',
            'recipient_list': [instance.card.user.email],
            'message': f'Пользователь {instance.user.username} оставил коментарий вашей карточке {instance.card.title}... \n'
                       f'{instance.content}',
        }

        send_notification.delay(email_data)


@receiver(post_save, sender=ThemeComments)
def notify(sender, instance, **kwargs):
    if instance.theme.user.is_receive_notifications:

        email_data = {
            'subject': f'Пользователь {instance.user.username} оставил коментарий вашей теме {instance.theme.title}...',
            'recipient_list': [instance.theme.user.email],
            'message': f'Пользователь {instance.user.username} оставил коментарий вашей карточке {instance.theme.title}... \n'
                       f'{instance.content}',
        }

        send_notification.delay(email_data)
