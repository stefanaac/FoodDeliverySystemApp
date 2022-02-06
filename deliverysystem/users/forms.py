from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



class RestaurantEditDetailsForm(forms.Form):
    restaurant_name = forms.CharField(label='phoneNumber')
    restaurant_address=forms.CharField(label='address')
    restaurant_opentime=forms.CharField(label='opentime')
    restaurant_closetime = forms.CharField(label='closetime')


