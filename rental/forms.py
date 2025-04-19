from django import forms 
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser,Brand,Car,Booking
from django.forms.widgets import DateInput

class UserSignupForm(UserCreationForm):
    class Meta:
        model=CustomUser
        fields=['email','phone','fullname','password1','password2']

class LoginForm(forms.Form):
    email=forms.EmailField()
    password=forms.CharField(widget=forms.PasswordInput)

class BrandForm(forms.ModelForm):
    class Meta:
        model=Brand
        fields=['name','description']

class CarForm(forms.ModelForm):
    class Meta:
        model=Car
        fields=['name','brand','model','price_per_day','image','availability']

class BookingForm(forms.ModelForm):
    class Meta:
        model=Booking
        fields=['start_date','end_date','location']
        widgets = {
            'start_date': DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Start Date'
            }),
            'end_date': DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'End Date'
            }),
        }

        labels = {
            'start_date': 'Start Date',
            'end_date': 'End Date',
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date should be after start date.")


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['fullname', 'email', 'phone', 'profile_pic']