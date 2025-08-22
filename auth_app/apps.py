from django.apps import AppConfig
from django.conf import settings

class AuthAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_app'
    def ready(self):
        from oauth2_provider.models import Application
        from django.db.utils import OperationalError, ProgrammingError

        try:
            # Create default OAuth2 application if none exists
            if not Application.objects.exists():
                Application.objects.create(
                    name="Default Google OAuth App",
                    client_type=Application.CLIENT_CONFIDENTIAL,
                    authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
                    redirect_uris=settings.GOOGLE_REDIRECT_URI,
                )
                print("✅ Created default OAuth2 application")
        except (OperationalError, ProgrammingError):
            # Happens before migrations, ignore
            pass