# Generated by Django 4.2 on 2023-07-02 09:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_themes_cards'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='themes',
            name='sub_theme_to',
        ),
        migrations.RemoveField(
            model_name='themes',
            name='user',
        ),
        migrations.DeleteModel(
            name='Cards',
        ),
        migrations.DeleteModel(
            name='Themes',
        ),
    ]
