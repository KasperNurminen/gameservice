from django.test import TestCase
from django.contrib.auth.models import Group, User

class PermissionsTestCase(TestCase):
    def setUp(self):
        group = Group.objects.get(name='developers')        
        self.developer = User.objects.create(username='developer', password='pass')
        self.player = User.objects.create(username='player', password='pass')
        self.developer.groups.add(group)

        self.developer.save()
        self.player.save()

    def test_developer_permissions(self):
        self.assertFalse(self.player.has_perm('gameservice.can_edit_games'))
        self.assertTrue(self.developer.has_perm('gameservice.can_edit_games'))