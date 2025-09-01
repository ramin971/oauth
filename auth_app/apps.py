from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate



def create_default_oauth_app(sender, **kwargs):
    try:
        # Import here so it happens only after migrations are applied
        from oauth2_provider.models import Application  

        if not Application.objects.exists():
            Application.objects.create(
                name="Default Google OAuth App",
                client_type=Application.CLIENT_CONFIDENTIAL,
                authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
                redirect_uris=settings.GOOGLE_REDIRECT_URI,
            )
            print("✅ Created default OAuth2 application")
    except Exception as e:
        print(f"⚠️ Could not create default OAuth2 app: {e}")



class AuthAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_app'
    def ready(self):
        post_migrate.connect(create_default_oauth_app, sender=self)
#        from oauth2_provider.models import Application
#        from django.db.utils import OperationalError, ProgrammingError
#
#        try:
            # Create default OAuth2 application if none exists
#            if not Application.objects.exists():
#                Application.objects.create(
#                    name="Default Google OAuth App",
#                    client_type=Application.CLIENT_CONFIDENTIAL,
#                    authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
#                    redirect_uris=settings.GOOGLE_REDIRECT_URI,
#                )
#                print("✅ Created default OAuth2 application")
#        except (OperationalError, ProgrammingError):
            # Happens before migrations, ignore
#            pass
