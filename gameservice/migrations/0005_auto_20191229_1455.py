# Generated by Django 3.0 on 2019-12-29 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameservice', '0004_auto_20191229_1451'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='categories',
        ),
        migrations.AddField(
            model_name='game',
            name='categories',
            field=models.ManyToManyField(to='gameservice.Category'),
        ),
    ]
