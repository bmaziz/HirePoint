from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Backend d'authentification personnalisé permettant la connexion
    via le nom d'utilisateur OU l'adresse e-mail.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        if username is None or password is None:
            return None

        # Recherche insensible à la casse sur username ou email
        try:
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # En cas de doublons rares, on filtre d'abord par username exact
            user = User.objects.filter(username__iexact=username).first()
            if not user:
                user = User.objects.filter(email__iexact=username).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
