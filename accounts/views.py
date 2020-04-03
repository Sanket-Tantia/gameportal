from django.shortcuts import render, redirect

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from .decorators import isathenticated_user, authorized_user

from datetime import datetime, date

from django.contrib import messages

from django.db import connection

from django.urls import reverse
from django.http import HttpResponseRedirect

from .forms import CreateUserForm, CreateProfileForm, TokenTransactionForm
from .models import AvailableToken, Profile, TokenTransaction, GrantedToken, GameRound

from datetime import datetime
from collections import defaultdict


@isathenticated_user
def loginPage(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
                if group == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('game_console')
        else:
            messages.info(request, 'Username or password is incorrect')

    return render(request, 'accounts/login.html', context)


@login_required(login_url='login')
def logoutPage(request):
    logout(request)
    response = redirect('login')
    response.delete_cookie('username')
    response.delete_cookie('session')
    return response


@login_required(login_url='login')
@authorized_user(allowed_roles=['admin'])
def createUserPage(request):
    context = {}
    if request.method == 'POST':
        print(request.POST)
        user_data = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'password1': request.POST.get('password1'),
            'password2': request.POST.get('password2')
        }
        user_form = CreateUserForm(user_data)

        if user_form.is_valid():
            username = user_form.cleaned_data.get('username')
            user = user_form.save()
            group = Group.objects.get(name='customer')
            user.groups.add(group)

            profile_data = {
                'username': user.id,
                'name': request.POST.get('name'),
                'probability': request.POST.get('probability') if request.POST.get('probability') else None
            }

            token_data = {
                'username': user.id,
                'session': request.session._session_key,
                'token_amount': request.POST.get('token_amount') if request.POST.get('token_amount') else 0,
                'is_token_purchased': True,
                'is_token_granted': False
            }

            profile_form = CreateProfileForm(profile_data)
            token_transaction_form = TokenTransactionForm(token_data)

            if profile_form.is_valid() and token_transaction_form.is_valid():
                profile_form.save()
                token_transaction_form.save()

                return redirect('admin_dashboard')
            else:
                # delete that user
                # User.objects.get(username=username).delete()
                if token_transaction_form.is_valid():
                    print("Profile form not valid", profile_form.errors)
                else:
                    print("Token form not valid",
                          token_transaction_form.errors)

        else:
            print("User form not valid", user_form.errors)

    return render(request, 'accounts/create_user.html', context)


@login_required(login_url='login')
@authorized_user(allowed_roles=['admin'])
def adminDashboard(request):
    if request.method == 'POST':
        new_probability = request.POST.get('probability', None)
        user_obj = User.objects.get(username=request.POST.get('username'))

        if new_probability:
            profile_obj = user_obj.profile_set.filter(is_active=True)[0]
            existing_probability = profile_obj.probability

            if int(new_probability) != existing_probability:
                with connection.cursor() as cursor:
                    if existing_probability:
                        cursor.execute("""UPDATE accounts_profile
                        SET is_active = 0, end_date = DATE(%s)
                        WHERE is_active = 1
                        AND username_id = %s
                        AND probability != %s""", [date.today(), user_obj.id, new_probability])
                    else:
                        cursor.execute("""UPDATE accounts_profile
                        SET is_active = 0, end_date = DATE(%s)
                        WHERE is_active = 1
                        AND username_id = %s""", [date.today(), user_obj.id])

                profile_data = {
                    'username': user_obj.id,
                    'name': profile_obj.name,
                    'probability': new_probability
                }
                profile_form = CreateProfileForm(profile_data)

                if profile_form.is_valid():
                    profile_form.save()
                else:
                    print("Profile form not valid", profile_form.errors)

        new_token_amount = request.POST.get('token_amount', None)
        if new_token_amount and int(new_token_amount) > 0:
            token_data = {
                'username': user_obj.id,
                'session': request.session._session_key,
                'token_amount': new_token_amount,
                'is_token_purchased': True,
                'is_token_granted': False
            }
            token_form = TokenTransactionForm(token_data)
            if token_form.is_valid():
                token_form.save()
            else:
                print("token form not valid", token_form.errors)

                # profile_obj = user_obj.profile_set.filter(is_active=True)
            # do_insert_flag = True
            # if profile_obj.count() > 0 and profile_obj[0].probability:
            #     if profile_obj[0].probability == int(new_probability):
            #         do_insert_flag = False

            # if do_insert_flag:
            #     with connection.cursor() as cursor:
            #         cursor.execute("""UPDATE accounts_profile SET is_active = 0,
            #         end_date = DATE(%s) WHERE is_active = 1
            #         AND username = %s""", [date.today(), user_obj.id])

            #     profile_data = {
            #         'username': user_obj.id,
            #         'name': profile_obj[0].name,
            #         'probability': new_probability
            #     }
            #     profile_form = CreateProfileForm(profile_data)

            #     if profile_form.is_valid():
            #         profile_form.save()
        return HttpResponseRedirect('/dashboard')

    all_users_detail, count = {}, 1

    for each_user in User.objects.filter(groups__name='customer'):
        all_users_detail[each_user.username] = {'count': count}

        if each_user.email:
            all_users_detail[each_user.username]['email'] = each_user.email
        else:
            all_users_detail[each_user.username]['email'] = 'NA'

        each_user_profile = each_user.profile_set.filter(is_active=True)

        if each_user_profile.count() > 0 and each_user_profile[0].probability:
            all_users_detail[each_user.username]['probability'] = each_user_profile[0].probability
        else:
            all_users_detail[each_user.username]['probability'] = 'NA'
            # if each_user_profile[0].name:
            #     all_users_detail[each_user.username]['name'] = each_user_profile[0].name

        each_user_token = AvailableToken.objects.filter(username=each_user.id)
        if each_user_token.count() > 0 and each_user_token[0].available_token:
            all_users_detail[each_user.username]['token_amount'] = each_user_token[0].available_token
        else:
            all_users_detail[each_user.username]['token_amount'] = 0
        count += 1

    context = {'all_users_detail': all_users_detail}
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required(login_url='login')
@authorized_user(allowed_roles=['admin'])
def transactionDashboard(request):
    purchase_token_history = TokenTransaction.objects.filter(
        is_token_purchased=True).order_by('username')

    all_users_purchase_token, count = defaultdict(list), 1
    for each_transaction in purchase_token_history:

        all_users_purchase_token[each_transaction.username.username].append({
            'count': count,
            'token_amount': each_transaction.token_amount,
            'date': each_transaction.transaction_date,
        })
        count += 1

    grant_token_history = TokenTransaction.objects.filter(
        is_token_granted=True).order_by('username')

    all_users_grant_token, count = defaultdict(list), 1
    for each_transaction in grant_token_history:

        all_users_grant_token[each_transaction.username.username].append({
            'count': count,
            'token_amount': each_transaction.token_amount,
            'date': each_transaction.transaction_date,
        })
        count += 1

    # print(all_users_purchase_token)
    context = {'all_users_purchase_token': dict(all_users_purchase_token),
               'all_users_grant_token': dict(all_users_grant_token)}
    return render(request, 'accounts/transaction_dashboard.html', context)


@login_required(login_url='login')
@authorized_user(allowed_roles=['admin', 'customer'])
def gameConsole(request):
    available_tokens = AvailableToken.objects.get(
        username=request.user.id).available_token

    if request.method == 'POST':
        is_valid_amount = True
        transaction_data = {
            'username': request.user.id,
            'session': request.session._session_key,
            'token_amount': request.POST.get('token_amount'),
            'is_token_purchased': False,
            'is_token_granted': True
        }
        token_transaction_form = TokenTransactionForm(transaction_data)

        if not request.POST.get('token_amount', False) or int(available_tokens) < int(request.POST.get('token_amount')) or int(request.POST.get('token_amount')) <= 0:
            is_valid_amount = False

        if token_transaction_form.is_valid() and is_valid_amount:
            token_transaction_form.save()
            context = {
                'granted_token': request.POST.get('token_amount'),
                'login_time': request.user.last_login,
                'available_tokens': available_tokens - int(request.POST.get('token_amount')),
                'my_session': request.session._session_key
            }
            try:
                context['granted_token'] = GrantedToken.objects.get(
                    session=request.session._session_key).granted_token
            except GrantedToken.DoesNotExist:
                pass
            return HttpResponseRedirect('/console')
            # return render(request, 'accounts/game_console.html', context)
        else:
            context = {
                'granted_token': 0,
                'login_time': request.user.last_login,
                'available_tokens': available_tokens,
                'my_session': request.session._session_key
            }
            return HttpResponseRedirect('/console')
            # return render(request, 'accounts/game_console.html', context)

    context = {
        'granted_token': 0,
        'login_time': request.user.last_login,
        'available_tokens': available_tokens,
        'my_session': request.session._session_key
    }

    try:
        context['granted_token'] = GrantedToken.objects.get(
            session=request.session._session_key).granted_token
    except GrantedToken.DoesNotExist:
        pass

    response = render(request, 'accounts/game_console.html', context)
    response.set_cookie('username', request.user.id)
    response.set_cookie('session', request.session._session_key)
    return response


@login_required(login_url='login')
@authorized_user(allowed_roles=['admin'])
def resultDashboard(request):
    context = {}
    game_history = GameRound.objects.all().order_by('username')

    all_users_summary_game_history = {}
    for each_game in game_history:
        if not all_users_summary_game_history.get(each_game.username.username, False):
            available_token = AvailableToken.objects.get(username=each_game.username.id).available_token
            all_users_summary_game_history[each_game.username.username] = {
                'total_games_played': 0,
                'total_games_won': 0,
                'total_tokens_won': 0,
                'available_token': available_token
            }

        all_users_summary_game_history[each_game.username.username]['total_games_played'] += 1
        if each_game.tokens_won > 0:
            all_users_summary_game_history[each_game.username.username]['total_games_won'] += 1
            all_users_summary_game_history[each_game.username.username]['total_tokens_won'] += each_game.tokens_won
    
    for each_user in  all_users_summary_game_history.keys():
        all_users_summary_game_history[each_user]['margin'] = 100*all_users_summary_game_history[each_user]['total_games_won']/all_users_summary_game_history[each_user]['total_games_played']

    # print(all_users_summary_game_history)

    all_users_detail_game_history = defaultdict(list)
    for each_game in game_history:
        all_users_detail_game_history[each_game.username.username].append({
            'session': each_game.session[0:40],
            'tokens_playing_for': each_game.tokens_playing_for,
            'tokens_won': each_game.tokens_won,
            'tokens_remaining': each_game.tokens_remaining,
            'won_on_number': each_game.won_on_number,
            'is_jackpot': each_game.is_jackpot,
            'date': each_game.insert_datetime,
        })

    context = {'all_users_detail_game_history': dict(
        all_users_detail_game_history),'all_users_summary_game_history':all_users_summary_game_history}
    return render(request, 'accounts/result.html', context)
