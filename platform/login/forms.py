# login/forms.py

from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput)

    destination = forms.CharField(max_length=100, required=False)
    age = forms.IntegerField(required=False)
    exchange_school = forms.CharField(max_length=100, required=False)

    start_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}),
        required=False,
        label='Start Date'
    )
    end_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}),
        required=False,
        label='End Date'
    )
    gender = forms.ChoiceField(choices=(('M', 'Male'), ('F', 'Female')), required=False)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'destination', 'age', 'exchange_school', 'start_date', 'end_date', 'gender', 'avatar')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    # check the validity of the dates
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('End date must be after the start date.')

        return cleaned_data


from .models import UserProfile
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile  # This should be UserProfile, not User
        fields = ['destination', 'age', 'exchange_school', 'start_date', 'end_date', 'gender', 'avatar']