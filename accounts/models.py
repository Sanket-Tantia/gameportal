from django.db import models
from django.contrib.auth.models import User

from datetime import datetime


class Profile(models.Model):
    username = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255)
    probability = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(
        default=datetime.strptime('9999-31-12', '%Y-%d-%m').date())


class TokenTransaction(models.Model):
    username = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    session = models.CharField(max_length=255)
    token_amount = models.PositiveIntegerField(default=0)
    is_token_purchased = models.BooleanField()
    is_token_granted = models.BooleanField()
    transaction_date = models.DateTimeField(auto_now_add=True)


class AvailableToken(models.Model):
    username = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    available_token = models.PositiveIntegerField()


class GameRound(models.Model):
    username = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    session = models.CharField(max_length=255)
    tokens_playing_for = models.IntegerField()
    tokens_won = models.IntegerField()
    tokens_remaining = models.IntegerField()
    won_on_number = models.IntegerField(blank=True, null=True)
    is_jackpot = models.BooleanField(default=False)
    insert_datetime = models.DateTimeField(auto_now_add=True)
