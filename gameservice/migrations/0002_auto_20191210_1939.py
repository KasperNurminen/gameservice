

#from https://stackoverflow.com/questions/25024795/django-1-7-where-to-put-the-code-to-add-groups-programmatically
from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from gameservice.models import Game

def add_group_permissions(self, schema):
    developers, created = Group.objects.get_or_create(name='developers')
    if created:
        ct = ContentType.objects.get_for_model(Game)
        permission, _ = Permission.objects.get_or_create(codename='can_edit_games',
                                    name='Can edit games',
                                    content_type=ct)
        developers.permissions.add(permission)

class Migration(migrations.Migration):

    dependencies = [
        ('gameservice', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_group_permissions)
    ]
