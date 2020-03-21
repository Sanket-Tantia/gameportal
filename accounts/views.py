from django.shortcuts import render, redirect

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from .decorators import isathenticated_user, authorized_user

from django.contrib import messages

from .forms import CreateUserForm, CreateProfileForm, TokenTransactionForm
from .models import AvailableToken, Profile, TokenTransaction


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
    return redirect('login')


@login_required(login_url='login')
@authorized_user(allowed_roles=['admin'])
def createUserPage(request):
    context = {}
    if request.method == 'POST':

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
                'probability': request.POST.get('probability')
            }

            token_data = {
                'username': user.id,
                'session': request.session._session_key,
                'token_amount': request.POST.get('token_amount'),
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
                User.objects.get(username=username).delete()
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
    all_users_detail = {}
    count = 1
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
    print(all_users_detail)
    context = {'all_users_detail': all_users_detail}

    return render(request, 'accounts/admin_dashboard.html', context)


@login_required(login_url='login')
@authorized_user(allowed_roles=['admin', 'customer'])
def gameConsole(request):
    context = {}
    return render(request, 'accounts/game_console.html', context)
