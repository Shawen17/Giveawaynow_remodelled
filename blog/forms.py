from .models import Comment
from django.forms import ModelForm, fields
from django import forms





class CommentForm(ModelForm):
    
    body = forms.CharField(label='',widget=forms.Textarea(attrs={
        
        'placeholder':'comment here',
        'cols':5,
        'rows':2
    }))
    class Meta:
        model = Comment
        fields= ('email','body')

