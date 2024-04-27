# login/forms.py

from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput)

    # class Meta:
    #     model = User
    #     fields = ('username', 'password', 'password2')

    destination = forms.CharField(max_length=100, required=False)
    age = forms.IntegerField(required=False)
    exchange_school = forms.CharField(max_length=100, required=False)
    date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), required=False)
    gender = forms.ChoiceField(choices=(('M', 'Male'), ('F', 'Female')), required=False)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'destination', 'age', 'exchange_school', 'date', 'gender', 'avatar')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
