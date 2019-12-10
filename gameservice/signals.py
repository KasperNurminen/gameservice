#from https://stackoverflow.com/questions/42743825/how-to-create-groups-and-assign-permission-during-project-setup-in-django
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from models import Game

def create_groups(sender, **kwargs):
    developers, _ = Group.objects.get_or_create(name='developers')
    ct = ContentType.objects.get_for_model(Game)
    permission = Permission.objects.get_or_create(codename='can_edit_games',
                                   name='Can edit games',
                                   content_type=ct)
    developers.permissions.add(permission)

