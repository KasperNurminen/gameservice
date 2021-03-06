from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from hashlib import md5

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
        
account_activation_token = AccountActivationTokenGenerator()



