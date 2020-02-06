from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from decimal import *
from gameservice.models import Game, Payment, Score, Category


class Command(BaseCommand):
    def handle(self, **options):
        # superuser
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')

        # käyttäjät
        testikayttaja = User.objects.create_user(
            'player', 'player@example.com', 'pass')
        testidevaaja = User.objects.create_user(
            'developer', 'developer@example.com', 'pass')
        group = Group.objects.get(name='developers')
        testidevaaja.save()
        testidevaaja.groups.add(group)
        testikayttaja.save()
        testidevaaja.save()
        # kategoriat
        rpg = Category(name="RPG")
        singleplayer = Category(name="Singleplayer")
        rpg.save()
        singleplayer.save()

        # pelit
        testipeli = Game(title="Testipeli", developer=testidevaaja,
                         price=Decimal(15.5), url="/static/games/game2.html")
        testipeli.save()
        testipeli.categories.add(rpg)
        testipeli.categories.add(singleplayer)
        testipeli.save()

        testipeli2 = Game(title="Testipeli2", developer=testidevaaja, price=Decimal(
            25.5), url="https://users.aalto.fi/~oseppala/game/example_game.html")
        testipeli2.save()
        testipeli2.categories.add(rpg)
        testipeli2.save()

        # score
        score1 = Score(player=testikayttaja, score=100, game=testipeli)
        score2 = Score(player=testikayttaja, score=200, game=testipeli)
        score1.save()
        score2.save()

        # payment

        payment = Payment(user=testikayttaja, price=testipeli.price,
                          game=testipeli, pid="123", sid="123")
        payment.save()
