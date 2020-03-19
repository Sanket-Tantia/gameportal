from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    UserListView,
    UserDetailView,
    UserCreateView,
    GameRoundListView,
    GameRoundCreateView,
    GrantTokenCreateView,
    GameUserDetailView
)


app_name = 'user'
urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('granttoken/', GrantTokenCreateView.as_view(), name='token-detail'),
    path('create/', UserCreateView.as_view(), name='user-create'),
    path('gameinfo/', GameUserDetailView.as_view(), name='user-gameinfo'),
    path('<str:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('gameround/<int:session_id>/', GameRoundListView.as_view(), name='gameround-detail'),
    path('gameround/create/', GameRoundCreateView.as_view(), name='gameround-create'),
]
