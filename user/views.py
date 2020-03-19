from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db import connection

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from datetime import date

from .serializers import (
    UserSerializer,
    GameRoundSerializer,
    WinningNoHistorySerializer,
    AvailableTokenTransactionSerializer,
    AggAvailableTokenSerializer
)
from .models import(
    User,
    GameRound,
    WinningNoHistory,
    AvailableTokenTransaction,
    AggAvailableToken
)

# Create your views here.


def get_object_User(user_id):
    try:
        return User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return None


def get_object_WinningNoHistory(user_id, is_active=1):
    return WinningNoHistory.objects.filter(user__exact=user_id, is_active=1)


def get_available_token(user_id):
    try:
        return AggAvailableToken.objects.get(user=user_id)
    except AggAvailableToken.DoesNotExist:
        return None


def get_granted_token(user_id, session_id, is_token_granted=1):
    return AvailableTokenTransaction.objects.filter(user__exact=user_id, session__exact=session_id, is_token_granted=1)


def get_gameRounds_for_session(session_id):
    return GameRound.objects.filter(session__exact=session_id)


class UserListView(APIView):
    def get(self, request):
        all_users = User.objects.filter(role__exact='customer')
        serializer = UserSerializer(all_users, many=True)
        return Response(serializer.data)


class UserDetailView(APIView):
    def get(self, request, user_id):
        singleUserTokens = get_available_token(user_id)
        singleUser = get_object_User(user_id)
        singleUserProbability = get_object_WinningNoHistory(user_id)

        if isinstance(singleUser, User):
            userSerializer = UserSerializer(singleUser)
            body = userSerializer.data

            if isinstance(singleUserTokens, AggAvailableToken):
                tokenSerializer = AggAvailableTokenSerializer(singleUserTokens)
                body.update(tokenSerializer.data)

            if singleUserProbability.count() == 1:
                probabilitySerializer = WinningNoHistorySerializer(
                    singleUserProbability, many=True)
                data = {
                    'probability': probabilitySerializer.data[0].get('probability')
                }
                body.update(data)

            responseBody = {'ResponseStatus': '200_OK',
                            'ResponseMessage': body}

            return Response(responseBody, status=status.HTTP_200_OK)

        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, user_id):
        # if updating available token
        if request.data.get('token_amount', False):
            insertTokenBody = {
                'user': user_id,
                'session': request.data.get('session_id'),
                'token_amount': request.data.get('token_amount'),
                'is_token_purchased': 1,
                'is_token_granted': 0
            }
            insertTokenSerializer = AvailableTokenTransactionSerializer(
                None, data=insertTokenBody)
            if insertTokenSerializer.is_valid():
                insertTokenSerializer.save()
            else:
                return Response(insertTokenSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # if updating probability
        if request.data.get('probability', False):

            singleUserProbability = get_object_WinningNoHistory(user_id)

            # already has a probability
            if singleUserProbability.count() == 1:

                probabilitySerializer = WinningNoHistorySerializer(
                    singleUserProbability, many=True)
                if probabilitySerializer.data[0].get('probability') == request.data.get('probability'):
                    print("Incoming Probability is same")
                else:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "UPDATE winning_no_history SET is_active = 0, end_date = DATE(%s) WHERE is_active = 1 AND user_id = %s", [date.today(), user_id])

            probabilityBody = {
                'user': user_id,
                'probability': request.data.get('probability')
            }
            probabilitySerializer = WinningNoHistorySerializer(
                None, data=probabilityBody)

            if probabilitySerializer.is_valid():
                probabilitySerializer.save()
            else:

                return Response(probabilitySerializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # singleUser = get_object_User(user_id)
        # serializer = UserSerializer(singleUser, data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse(status=status.HTTP_200_OK)


class UserCreateView(APIView):
    def post(self, request):
        userSerializedData = UserSerializer(data=request.data)

        if userSerializedData.is_valid():
            userSerializedData.save()
            try:
                # if inserting probability
                if request.data.get('probability', False):
                    newProbabilityData = {
                        "user": request.data.get('user_id'),
                        "probability": request.data.get('probability'),
                    }

                    newProbabilitySerialized = WinningNoHistorySerializer(
                        data=newProbabilityData)

                    if newProbabilitySerialized.is_valid():
                        newProbabilitySerialized.save()
                        responseBody = {'ResponseStatus': '201_CREATED'}
                        return Response(responseBody, status=status.HTTP_201_CREATED)
                    else:
                        get_object_User(request.data.get('user_id')).delete()
                        return Response(newProbabilitySerialized.errors, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                get_object_User(request.data.get('user_id')).delete()
                return Response(newProbabilitySerialized.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(userSerializedData.errors, status=status.HTTP_400_BAD_REQUEST)


class GameRoundListView(APIView):
    def get(self, request, session_id):
        allGameRoundForSession = get_gameRounds_for_session(session_id)
        serializer = GameRoundSerializer(allGameRoundForSession, many=True)
        responseBody = {'ResponseStatus': '200_OK',
                        'ResponseMessage': serializer.data}
        return Response(responseBody, status=status.HTTP_200_OK)


class GameRoundCreateView(APIView):
    def post(self, request):
        serializer = GameRoundSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            responseBody = {'ResponseStatus': '201_CREATED'}
            return Response(responseBody, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GrantTokenCreateView(APIView):
    def post(self, request):
        insertTokenBody = {
            'user': request.data.get('user_id'),
            'session': request.data.get('session_id'),
            'token_amount': request.data.get('token_amount'),
            'is_token_purchased': 0,
            'is_token_granted': 1
        }
        insertTokenSerializer = AvailableTokenTransactionSerializer(
            None, data=insertTokenBody)
        if insertTokenSerializer.is_valid():
            insertTokenSerializer.save()
            responseBody = {'ResponseStatus': '201_CREATED'}
            return Response(responseBody, status=status.HTTP_201_CREATED)
        return Response(insertTokenSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameUserDetailView(APIView):
    def post(self, request):
        session_id = request.data.get('session_id')
        user_id = request.data.get('user_id')
        probability = None
        token_granted = 0

        tokensGrantedQuerySet = get_granted_token(user_id, session_id)
        singleUserProbability = get_object_WinningNoHistory(user_id)

        if tokensGrantedQuerySet.count() == 1:
            tokensGrantedSerializer = AvailableTokenTransactionSerializer(
                tokensGrantedQuerySet, many=True)
            token_granted = tokensGrantedSerializer.data[0].get('token_amount')

        if singleUserProbability.count() == 1:
            probabilitySerializer = WinningNoHistorySerializer(
                singleUserProbability, many=True)
            probability = probabilitySerializer.data[0].get('probability')

        body = {
            'user_id': user_id,
            'session_id': session_id,
            'token_granted': token_granted,
            'probability': probability
        }

        responseBody = {'ResponseStatus': '200_OK', 'ResponseMessage': body}
        return Response(responseBody, status=status.HTTP_200_OK)
