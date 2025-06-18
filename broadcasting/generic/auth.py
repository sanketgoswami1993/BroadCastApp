from django.contrib.auth.models import User
from django.utils.six import text_type
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from rest_framework.authtoken.models import Token
from rest_framework import HTTP_HEADER_ENCODING, exceptions

class GetUserRequested(object):
    token_model = Token
    user_model = User

    def authenticate_email_or_ph(self, email="", password="", **kwargs):
        try:
            user = self.user_model.objects.get(Q(email=email) | Q(user_rel__contact_num=email))
            if user.check_password(password):
                return user
            else:
                return None
        except:
            return None

    def get_user(self, request):
        return self.get_user_by_token(self.get_authenticated_token(request))

    def get_user_by_token(self, token):
        try:
            return self.token_model.objects.get(key=token).user
        except:
            return None

    def get_authorization_header(self, request):
        """
        Return request's 'Authorization:' header, as a bytestring.
        Hide some test client ickyness where the header can be unicode.
        """
        auth = request.META.get('HTTP_AUTHORIZATION', b'')
        if isinstance(auth, text_type):
            # Work around django test client oddness
            auth = auth.encode(HTTP_HEADER_ENCODING)
        return auth

    def get_authenticated_token(self, request):
        auth = self.get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            return None

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return token

    def create_token(self, user):
        token, created = self.token_model.objects.get_or_create(user=user)
        return token