from django.shortcuts import render , get_object_or_404
from .forms import LoginForm , RegisterForm , UserEditForm , ProfileEditForm
from django.contrib.auth import login , authenticate
from django.http import HttpResponse , JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from common.decorators import ajax_required
from .models import Profile , Contact
from django.contrib import messages
from django.contrib.auth.models import User
from actions.utils import create_action
from actions.models import Action



# Create your views here.

# def user_login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(request,username=cd['username'],password=cd['password'])
#             if user is not None:
#                 if user.is_active:
#                     login(request,user)
#                     return HttpResponse('You are loged in successfully')
#                 else:
#                     return HttpResponse('You are banned!')
#             else:
#                 return HttpResponse('Invalid Login!')
#     else:
#         form = LoginForm()
#     return render(request, 'account/login.html',{'form':form})

@login_required()
def dashboard(request):
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id',flat=True)
    if following_ids:
        actions = actions.filter(user_id__in=following_ids)
    else:
        actions = []
    actions = actions[:10]
    return render(request,'account/dashboard.html',{"actions":actions})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['password'] == form.cleaned_data['password2']:
                new_user = form.save(commit=False)
                new_user.set_password(
                    form.cleaned_data['password']
                )
                new_user.save()
                Profile.objects.create(user=new_user)
                create_action(new_user,'has ctreate account')
                
                return render(request,'account/register_done.html',{'new_user':new_user})
    else:
        form = RegisterForm()
    return render(request,'account/register.html',{'form':form})

@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,data=request.POST,files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Good it was successfully!')
        else:
            messages.error(request,'An error is happend!')

    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request, 'account\edit.html',{"user_form":user_form,"profile_form":profile_form})


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True).order_by('-date_joined')
    return render(request,'account/user/list.html',{"users":users})

@login_required
def user_detail(request,username):
    user = get_object_or_404(User,username=username,is_active=True)
    return render(request,'account/user/detail.html',{"user":user})

@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from = request.user,
                    user_to = user)

                create_action(request.user,'is following',user)
            else:
                Contact.objects.filter(user_from=request.user,user_to=user).delete()
            return JsonResponse({'status':'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status':'error'})
    else:
        return JsonResponse({'status':'error'})
