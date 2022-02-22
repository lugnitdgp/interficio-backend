from django.urls import path, include
from backend import views
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'users', views.UserViewSet, base_name='user')

urlpatterns = router.urls

urlpatterns += [
    path('scoreboard/', views.leaderboard, name="leaderborad"),
    path('auth/register/', views.RegistrationAPI.as_view(), name="auth-reg"),
    path('auth/login/', views.LoginAPI.as_view(), name="auth-login"),
    path('auth/changepassword/', views.ChangePasswordAPI.as_view(), name="auth-changepass"),
    path('player/', views.PlayerDetail.as_view(), name="palyer-detail"),
    path('getlevel/', views.GetLevel.as_view(), name="get-level"),
    path('getlevelclues/', views.GetLevelClues.as_view(), name="get-level-clues"),
    path('getclues/', views.GetClues.as_view(), name="get-clues"),
    path('unlockclue/', views.UnlockClue.as_view(), name="unlock-clues"),
    path('submit/ans/', views.SubmitLevelAns.as_view(), name="submit-ans"),
    path('submit/location/', views.SubmitLocation.as_view(), name="submit-location"),
    path('finaltext/', views.FinalText.as_view(), name="final-text"),
    path('getanswers/', views.GetPlayerAnswers.as_view(), name="get-answers"),
]
