from django import forms
from django.contrib.auth.models import User
from .models import Iot
import re
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    

    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1', 'password2']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match("^[a-zA-Z0-9]*$", first_name):
            raise ValidationError("First name must not contain special characters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match("^[a-zA-Z0-9]*$", last_name):
            raise ValidationError("Last name must not contain special characters.")
        return last_name
class IotForm(forms.ModelForm):
    class Meta:
        model = Iot
        fields = ['code']

    def clean_code(self):
        code = self.cleaned_data.get('code')

        if not code.startswith("1800") or not re.match(r'^[0-9]*$', code) or len(code) != 8:
            raise forms.ValidationError("IoT code is invalid.")

        return code
    
class IrisPredictionForm(forms.Form):
    temperature = forms.FloatField()
    humidity = forms.FloatField()
    soil_moisture_level = forms.FloatField()
