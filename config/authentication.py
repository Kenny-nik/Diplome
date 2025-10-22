from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


class JWTAuth(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    refresh['email'] = user.email
    refresh['role'] = user.role

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }