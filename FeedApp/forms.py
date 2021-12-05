from django import forms
from .models import Post, Profile, Relationship

class PostForm(forms.ModelForm):
    class Meta:
        mdoel = Post
        fields = ['description', 'image'] 
        labels = {'description': "What would you like to say?"} #blank form labels???
    
class ProfileForm(forms.ModelForm):
    class Meta:
        mdoel = Profile
        fields = ['first_name', 'last_name', 'email', 'dob', 'bio'] # fields displayed on the webpage
        labels = {'first_name': 'First Name', 
                    'last_name': 'Last Name', 
                    'email': 'Email', 
                    'dob': 'Date of Birth', 
                    'bio': 'Bio'} #old lable:new label displayed on the webpage

class RelationshipForm(forms.ModelForm):
    class Meta:
        mdoel = Relationship
        fields = '__all__'
        labels = {
            'sender': 'Accept friend request from:',
            'receiver': 'Send friend request to:',
            # 'status': 
            } 
        
        