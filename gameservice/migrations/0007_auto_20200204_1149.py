# Generated by Django 3.0.2 on 2020-02-04 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameservice', '0006_auto_20191229_1850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='url',
            field=models.CharField(max_length=200),
        ),
    ]
