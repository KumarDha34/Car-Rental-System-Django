from django import forms 
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser,Brand,Car,Booking
from django.forms.widgets import DateInput
from datetime import date,timedelta

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
        model = Booking
        fields = ['start_date', 'end_date', 'location']
        widgets = {
            'start_date': DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': date.today().isoformat(),  # Disable past dates
                'placeholder': 'Start Date',
                'min': date.today().strftime('%Y-%m-%d')
            }),
            'end_date': DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': date.today().isoformat(),  # Disable past dates
                'placeholder': 'End Date',
                'min': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
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

        if start_date and start_date < date.today():
            self.add_error('start_date', "Start date cannot be in the past.")

        if end_date and end_date < date.today():
            self.add_error('end_date', "End date cannot be in the past.")

        if start_date and end_date and start_date > end_date:
            self.add_error('end_date', "End date should be after start date.")


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['fullname', 'email', 'phone', 'profile_pic']