# Generated by Django 4.2 on 2023-06-26 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_options_user_if_private_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='if_private',
            field=models.BooleanField(default=False, verbose_name='Приватный ?'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_email_verified',
            field=models.BooleanField(default=False, verbose_name='Почта подтверденна?'),
        ),
    ]