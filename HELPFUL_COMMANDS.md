##These may come in use later
```
python3 manage.py shell
from django.contrib.auth.models import User
from decimal import *
testikayttaja = User(username="testi", password="pass")
testipeli = Game(title="Testipeli", developer=testikayttaja, price=Decimal(15.5), url="https://example.com")
testikayttaja.save()
testipeli.save()

#myöhemmin
Game.objects.get(title="Testipeli").delete()
User.objects.get(username="testi").delete()
```