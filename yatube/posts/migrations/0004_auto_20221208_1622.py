# Generated by Django 2.2.19 on 2022-12-08 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20221208_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.TextField(max_length=100),
        ),
    ]
