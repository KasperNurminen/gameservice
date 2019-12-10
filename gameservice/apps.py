from django.apps import AppConfig
from django.db.models.signals import post_migrate
from signals import create_groups

class GameserviceConfig(AppConfig):
    name = 'gameservice'

    def ready(self):
        post_migrate.connect(create_groups, sender=self)
