from django.urls import path, include
from backend import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'users', views.UserViewSet, base_name='user')
router.register(r'level', views.LevelViewSet)

urlpatterns = router.urls;

urlpatterns += [
    path('leaderboard/', views.leaderboard, name="leaderborad"),
]