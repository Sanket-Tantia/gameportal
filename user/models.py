from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from datetime import datetime
# Create your models here.


class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=25)
    created_date = models.DateField(auto_now_add=True)
    created_by = models.CharField(max_length=100)
    last_modified_date = models.DateField(auto_now=True)
    last_modified_by = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'user'

    def get_absolute_url(self):
        return reverse("user:user-detail", kwargs={"user_id": self.user_id})


class WinningNoHistory(models.Model):
    auto_field = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING)
    probability = models.IntegerField()
    is_active = models.IntegerField(default=1)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(
        default=datetime.strptime('9999-31-12', '%Y-%d-%m').date())

    class Meta:
        managed = False
        db_table = 'winning_no_history'


class AvailableTokenTransaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    session = models.ForeignKey('Sessions', models.DO_NOTHING)
    token_amount = models.IntegerField()
    is_token_purchased = models.IntegerField()
    is_token_granted = models.IntegerField()
    transaction_date = models.DateField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'available_token_transaction'


class AggAvailableToken(models.Model):
    user = models.OneToOneField('User', models.DO_NOTHING, primary_key=True)
    available_token = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'agg_available_token'


class Sessions(models.Model):
    session_id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    session_log_in_time = models.DateTimeField(blank=True, null=True)
    session_log_out_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sessions'


class GameRound(models.Model):
    round_id = models.AutoField(primary_key=True)
    session = models.ForeignKey('Sessions', models.DO_NOTHING)
    tokens_playing_for = models.IntegerField()
    tokens_won = models.IntegerField()
    tokens_remaining = models.IntegerField()
    won_on_number = models.IntegerField(blank=True, null=True)
    is_jackpot = models.IntegerField()
    insert_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'game_round'

    def get_absolute_url(self):
        return reverse("user:gameround-detail", kwargs={"session": self.session})
