from django.urls import include, path
from rest_framework import routers
from .views import GameViewSet, UserViewSet, GroupViewSet

router = routers.DefaultRouter()
router.register(r'game', GameViewSet)
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
