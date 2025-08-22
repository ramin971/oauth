import requests
# from django.contrib.auth.models import User
from .models import User
from oauth2_provider.models import Application, AccessToken, RefreshToken
from oauthlib.common import generate_token
from oauth2_provider.settings import oauth2_settings
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .serializers import UserSerializer
from django.conf import settings

class GoogleAuthInit(APIView):
    permission_classes = []  # Public endpoint

    def get(self, request):
        url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={settings.GOOGLE_CLIENT_ID}&"
            f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
            "response_type=code&"
            "scope=email profile"
        )
        return Response({"auth_url": url})


class GoogleAuthCallback(APIView):
    permission_classes = []  # Public endpoint

    def get(self, request):
        code = request.GET.get("code")

        # Exchange code for access_token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        r = requests.post(token_url, data=data)
        token_data = r.json()
        google_access_token = token_data.get("access_token")

        # Get user info from Google
        userinfo = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {google_access_token}"}
        ).json()

        email = userinfo.get("email")
        name = userinfo.get("name") or email.split("@")[0]  # fallback if name is missing


        # Create or get user
        user, created = User.objects.get_or_create(
            username=email,
            defaults={"first_name": name}
        )

        # Create DOT token
        application, _ = Application.objects.get_or_create(
            name="Default Google OAuth App",
            defaults={
                "client_type": Application.CLIENT_CONFIDENTIAL,
                "authorization_grant_type": Application.GRANT_AUTHORIZATION_CODE,
                "redirect_uris": settings.GOOGLE_REDIRECT_URI,
            }
        )

        expires = timezone.now() + timedelta(days=1)

        access_token = AccessToken.objects.create(
            user=user,
            application=application,
            # token=oauth2_settings.ACCESS_TOKEN_GENERATOR(request),
            token=generate_token(),
            expires=expires,
            scope="read write",
        )

        refresh_token = RefreshToken.objects.create(
            user=user,
            # token=oauth2_settings.REFRESH_TOKEN_GENERATOR(request),
            token=generate_token(),
            application=application,
            access_token=access_token,
        )

        return Response({
            "access_token": access_token.token,
            "refresh_token": refresh_token.token,
            "token_type": "Bearer",
            "expires_in": 86400,
            "user": {
                "id": user.id,
                "email": user.username,
                "name": user.first_name,
            }
        })



class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False , methods=['get','patch','delete'],permission_classes=[IsAuthenticated])
    def me(self,request):
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data,status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            serializer = UserSerializer(user,data=request.data,partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,status=status.HTTP_205_RESET_CONTENT)

        elif request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)