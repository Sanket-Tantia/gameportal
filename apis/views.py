from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db import connection

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from accounts.models import GameRound, Profile, AvailableToken, TokenTransaction
from .serializers import GameRoundSerializer


class GameRoundListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, session):
        all_rounds = GameRound.objects.filter(session=session)
        serializer = GameRoundSerializer(all_rounds, many=True)
        responseBody = {'ResponseStatus': '200_OK',
                        'ResponseMessage': serializer.data}
        return Response(responseBody, status=status.HTTP_200_OK)


class GameRoundCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = GameRoundSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            responseBody = {'ResponseStatus': '201_CREATED'}
            return Response(responseBody, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserGameProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        session = request.data.get('session')
        username = request.data.get('username')
        probability = None
        token_granted = 0

        user_granted_token = TokenTransaction.objects.filter(
            session=session, is_token_granted=True)
        if user_granted_token.count() > 0 and user_granted_token[0].token_amount:
            token_granted = user_granted_token[0].token_amount

        user_probability = Profile.objects.filter(
            username=username, is_active=True)
        if user_probability.count() > 0 and user_probability[0].probability:
            probability = user_probability[0].probability

        body = {
            'username': username,
            'session': session,
            'token_granted': token_granted,
            'probability': probability
        }

        responseBody = {'ResponseStatus': '200_OK', 'ResponseMessage': body}
        return Response(responseBody, status=status.HTTP_201_CREATED)
