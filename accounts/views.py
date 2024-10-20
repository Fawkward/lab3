from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from .utils import log_audit_action
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.shortcuts import render
from django.http import JsonResponse
from .models import Comment
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Comment
from django.shortcuts import render, redirect

import json
comments = []

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('comments')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                log_audit_action(user, f"Успішний вхід в систему")
                return redirect('comments')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def success_login(request):
    return render(request, 'accounts/comments.html')

def success_register(request):
    return render(request, 'accounts/comments.html')



from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Comment

class UserGroupForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True)

@login_required(login_url='/login/')
def comments_view(request):
    is_admin = request.user.groups.filter(name='Admin').exists()
    is_moderator = request.user.groups.filter(name='Moderator').exists()

    if request.method == "POST":
        comment_text = request.POST.get("comment")
        if comment_text:
            Comment.objects.create(user=request.user, text=comment_text)
            log_audit_action(request.user , f"Написав коментар: {comment_text}")
            return redirect('comments')

        if is_admin:
            user_id = request.POST.get('user_id')
            group_id = request.POST.get('group_id')

            try:
                user = User.objects.get(id=user_id)
                group = Group.objects.get(id=group_id)
                if user != request.user:
                    user.groups.clear()
                    user.groups.add(group)
                    log_audit_action(request.user, f"Змінив рівень доступу користувача {user.username} на '{group.name}'.")
                    messages.success(request, f"Группа пользователя {user.username} изменена на {group.name}.")
            except User.DoesNotExist:
                messages.error(request, "Пользователь не найден.")
            except Group.DoesNotExist:
                messages.error(request, "Группа не найдена.")

            return redirect('comments')

    comments = Comment.objects.all().order_by('-created_at')
    user_group_form = UserGroupForm()

    return render(request, 'accounts/comments.html', {
        'comments': comments,
        'is_admin': is_admin,
        'is_moderator': is_moderator,
        'user_group_form': user_group_form,
        'user': request.user
    })


from django.shortcuts import render
from .models import AuditLog

@login_required(login_url='/login/')
def audit_log_view(request):
    if not request.user.groups.filter(name='Admin').exists():
        return redirect('comments')

    logs = AuditLog.objects.all().order_by('-action_time')
    return render(request, 'accounts/audit_log.html', {'logs': logs})


@login_required(login_url='/login/')
def delete_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if (comment.user == request.user or # polezno
        request.user.groups.filter(name='Admin').exists() or
        request.user.groups.filter(name='Moderator').exists()):
        comment.delete()
        log_audit_action(request.user, f"Видалив коментар користувача {comment.user}: {comment.text}")
        return redirect('comments')
    else:
        return redirect('comments')

@csrf_exempt
def add_comment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        comment = Comment.objects.create(user=request.user, text=data['text'])
        return JsonResponse({'status': 'success', 'comment': comment.text, 'user': comment.user.username})
    return JsonResponse({'status': 'fail'}, status=400)
