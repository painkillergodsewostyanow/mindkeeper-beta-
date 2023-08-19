import os

from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save

from mindkeeper.settings import MEDIA_ROOT, MEDIA_URL
from users.models import User
from .models import Cards, Themes


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


@receiver(post_save, sender=Cards)
def post_save_card(sender, instance, created, update_fields, **kwargs):
    instance.update_search_vector('title', 'content')

