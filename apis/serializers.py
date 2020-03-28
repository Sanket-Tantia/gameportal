from rest_framework import serializers
from accounts.models import GameRound, TokenTransaction


class GameRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRound
        fields = ('username', 'session', 'tokens_playing_for', 'tokens_won',
                  'tokens_remaining', 'won_on_number', 'is_jackpot')


class TokenTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenTransaction
        fields = ('username', 'session', 'token_amount',
                  'is_token_purchased', 'is_token_granted')
