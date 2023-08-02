# Generated by Django 4.2 on 2023-08-02 08:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_alter_cardcomments_obj_alter_themecomments_obj'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardcomments',
            name='obj',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.cards'),
        ),
        migrations.AlterField(
            model_name='comments',
            name='sub_comment_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.comments'),
        ),
        migrations.AlterField(
            model_name='themecomments',
            name='obj',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.themes'),
        ),
    ]
