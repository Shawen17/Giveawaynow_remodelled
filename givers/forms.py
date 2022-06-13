from django.db import models
from django.core.exceptions import ValidationError
from django.forms.models import ALL_FIELDS
from .models import Give,Profile,ContactUs,states,Vendor,Location,PickupCentre,State,validate_number
from django.forms import ModelForm, fields
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django_select2.forms import ModelSelect2Widget
from .fields import GroupedModelChoiceField


class ContactUsForm(ModelForm):
    
    class Meta:
        model= ContactUs
        fields = ('email','subject','ticket','body')


class GiveForm(ModelForm):
    
    class Meta:
        model= Give
        fields = ('description','category','image','gender','quantity')
    
class SignupForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password Again'}))
    email = forms.EmailField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Email'}))
    first_name = forms.CharField(max_length= 100,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'}))
    last_name = forms.CharField(max_length= 100,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'}))
    username = forms.CharField(max_length= 200,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}))
    phone_number=forms.IntegerField(required=True)
    class Meta:
        model = User
        fields = ('first_name','last_name','username','email','phone_number','password1','password2')
    
    


class Profileform(ModelForm):
    
    class Meta:
        model = Profile
        fields = ('profile_pic','sex','state','phone_number')

class VendorForm(GiveForm,ModelForm):
    #state=forms.ChoiceField(widget=forms.Select(attrs={'placeholder':'State of Residence'}),choices=states)
    receiver_number=forms.IntegerField(validators=[validate_number])
    class Meta:
        model = Vendor
        fields=('receiver_number','delivery_address')


class PickupPointForm(ModelForm):
    pickup_centre = GroupedModelChoiceField(
        queryset=PickupCentre.objects.exclude(state=None), 
        choices_groupby='state'
    )

    class Meta:
         model = Location
         fields = ('pickup_centre',)

    