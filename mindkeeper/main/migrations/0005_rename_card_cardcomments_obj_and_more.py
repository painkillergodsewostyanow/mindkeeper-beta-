# Generated by Django 4.2 on 2023-07-22 09:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_rename_card_cardlikes_obj_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cardcomments',
            old_name='card',
            new_name='obj',
        ),
        migrations.RenameField(
            model_name='cardviews',
            old_name='card',
            new_name='obj',
        ),
        migrations.RenameField(
            model_name='themecomments',
            old_name='theme',
            new_name='obj',
        ),
        migrations.RenameField(
            model_name='themeviews',
            old_name='theme',
            new_name='obj',
        ),
    ]
