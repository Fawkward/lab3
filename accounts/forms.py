# accounts/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем стандартные help_text
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        # Отключаем стандартные сообщения об ошибках
        self.fields['username'].required = False
        self.fields['password1'].required = False
        self.fields['password2'].required = False


from django import forms
from django.contrib.auth.models import Group

class UserGroupForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True)
