from django.urls import path
from .views import (
    createUserPage,
    loginPage,
    adminDashboard,
    gameConsole,
    logoutPage,
    transactionDashboard,
    resultDashboard
)

urlpatterns = [
    path('create/', createUserPage, name='create_user'),
    path('login/', loginPage, name='login'),
    path('logout/', logoutPage, name='logout'),
    path('dashboard/', adminDashboard, name='admin_dashboard'),
    path('transaction/', transactionDashboard, name='transaction_dashboard'),
    path('console/', gameConsole, name='game_console'),
    path('result/', resultDashboard, name='result_dashboard'),
]
