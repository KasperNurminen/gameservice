from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from decimal import *
from gameservice.models import Game, Payment, Score, Category


class Command(BaseCommand):
    def handle(self, **options):
        # superuser
        User.objects.create_superuser('admin', 'admin@example.com', 'adm1n1')

        # käyttäjät
        testikayttaja = User.objects.create_user(
            'player', 'player@example.com', 'ple1jeri')
        testidevaaja = User.objects.create_user(
            'developer', 'developer@example.com', 'develoupper1')
        otto = User.objects.create_user(
            'otto', 'otto@example.com', 'develoupper2')
        group = Group.objects.get(name='developers')
        testidevaaja.save()
        testidevaaja.groups.add(group)
        otto.groups.add(group)
        otto.save()
        testikayttaja.save()
        testidevaaja.save()
        # kategoriat
        rpg = Category(name="RPG")
        rpg.save()
        action = Category(name="Action")
        action.save()
        sport = Category(name="Sport")
        sport.save()
        puzzle = Category(name="Puzzle")
        puzzle.save()

        # pelit
        testipeli = Game(title="Oma peli", developer=testidevaaja,
                         price=Decimal(15.5), url="../static/games/game2.html")
        testipeli.save()
        testipeli.categories.add(puzzle)
        testipeli.save()

        testipeli2 = Game(title="Oton peli", developer=otto, price=Decimal(
            25.5), url="https://users.aalto.fi/~oseppala/game/example_game.html")
        testipeli2.save()
        testipeli2.categories.add(rpg)
        testipeli2.categories.add(action)
        testipeli2.save()

        # score
        score1 = Score(player=testikayttaja, score=10, game=testipeli)
        score1.save()

        # payment

        payment = Payment(user=testidevaaja, price=testipeli.price,
                          game=testipeli, pid="123", sid="123")
        payment.save()
