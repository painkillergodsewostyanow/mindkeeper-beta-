# Generated by Django 4.2 on 2023-07-14 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cardaccess',
            options={'verbose_name': 'Доступ к карточке', 'verbose_name_plural': 'Доступ к карточкам'},
        ),
        migrations.AlterModelOptions(
            name='themeaccess',
            options={'verbose_name': 'Доступ к теме', 'verbose_name_plural': 'Доступ к темам'},
        ),
        migrations.AddField(
            model_name='cards',
            name='views',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='themes',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]
