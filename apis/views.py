from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db import connection

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from accounts.models import GameRound, Profile, AvailableToken, TokenTransaction, GrantedToken
from .serializers import GameRoundSerializer, TokenTransactionSerializer

from django.contrib.auth import authenticate

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

        try:
            token_granted = GrantedToken.objects.get(
                session=session).granted_token
        except GrantedToken.DoesNotExist:
            pass

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
        return Response(responseBody, status=status.HTTP_200_OK)


class UserRefillTokenView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        transaction_data = {
            'username': request.data.get('username'),
            'session': request.data.get('session'),
            'token_amount': request.data.get('token_amount'),
            'is_token_purchased': False,
            'is_token_granted': True
        }
        serializer = TokenTransactionSerializer(data=transaction_data)
        if serializer.is_valid():
            serializer.save()
            responseBody = {'ResponseStatus': '200_OK'}
            return Response(responseBody, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAuthorizeRefillView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = authenticate(request, username=request.data.get('username'), password=request.data.get('password'))
        if user is not None:
            try:
                available_token = AvailableToken.objects.get(username=user.id).available_token
            except AvailableToken.DoesNotExist:
                available_token = 0
            
            body = {
                'username': user.username,
                'available_token': available_token
            }

            responseBody = {'ResponseStatus': '200_OK', 'ResponseMessage': body}
            return Response(responseBody, status=status.HTTP_200_OK)
        else:
            responseBody = {'ResponseStatus': '401_UNAUTHORIZED', 'ResponseMessage': "Username or password is incorrect"}
            return Response(responseBody, status=status.HTTP_401_UNAUTHORIZED)