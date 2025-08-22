from django.urls import path, include
from rest_framework import routers
from oauth2_provider import urls as oauth2_urls
from .views import UserViewSet, GoogleAuthInit, GoogleAuthCallback

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)



urlpatterns = [
    path('o/', include(oauth2_urls)),
    path('', include(router.urls)),
    # Google OAuth
    path('auth/google/init/', GoogleAuthInit.as_view(), name="google-init"),
    path('auth/google/callback/', GoogleAuthCallback.as_view(), name="google-callback"),
]