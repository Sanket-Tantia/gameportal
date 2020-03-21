from django.urls import path
from .views import (
    createUserPage,
    loginPage,
    adminDashboard,
    gameConsole,
    logoutPage
)

urlpatterns = [
    path('create/', createUserPage, name='create_user'),
    path('login/', loginPage, name='login'),
    path('logout/', logoutPage, name='logout'),
    path('dashboard/', adminDashboard, name='admin_dashboard'),
    path('console/', gameConsole, name='game_console'),
]
