from rest_framework import serializers
from accounts.models import GameRound


class GameRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRound
        fields = ('username', 'session', 'tokens_playing_for', 'tokens_won',
                  'tokens_remaining', 'won_on_number', 'is_jackpot', 'insert_datetime')
