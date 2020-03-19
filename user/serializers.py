from rest_framework import serializers
from .models import (
    User,
    GameRound,
    WinningNoHistory,
    AvailableTokenTransaction,
    AggAvailableToken
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'name', 'password',
                  'email', 'role', 'created_by', 'last_modified_by')
        # fields = '__all__'


class GameRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRound
        fields = ('session', 'tokens_playing_for', 'tokens_won',
                  'tokens_remaining', 'won_on_number', 'is_jackpot')


class WinningNoHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WinningNoHistory
        fields = ('user', 'probability', 'is_active', 'end_date')


class AvailableTokenTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableTokenTransaction
        fields = ('user', 'session', 'token_amount',
                  'is_token_purchased', 'is_token_granted')


class AggAvailableTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggAvailableToken
        fields = ('user', 'available_token')
