# Generated by Django 2.2.9 on 2023-01-05 12:06

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20221211_1825'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-pub_date',)},
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True,
                                    help_text='Выберите группу поста',
                                    null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='posts', to='posts.Group'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Введите текст поста',
                                   validators=[django.core.validators.MaxLengthValidator(250,
                                               'Превышено максимальное количество символов')]),
        ),
    ]
