from django.shortcuts import render, redirect
from .forms import PostForm, ProfileForm, RelationshipForm
from .models import Post, Comment, Like, Profile, Relationship
from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.http import Http404


# Create your views here.

# When a URL request matches the pattern we just defined, 
# Django looks for a function called index() in the views.py file.

def index(request):
    """ The home pate for FeedApp. """
    return render(request, 'FeedApp/index.html')



@login_required #only after logging in, can access the profile funciton(protection)
def profile(request):
    profile = Profile.objects.filter(user=request.user) # only user that logged on can access information of their own.
    if not profile.exists():
        Profile.objects.create(user=request.user)
    profile = Profile.objects.get(user=request.user) # can use get() only when we are sure the user exists

    if request.method != 'POST':
        form =ProfileForm(instance=profile) 
    else:
        form = ProfileForm(instance=profile,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('FeedApp:profile')
        
    context = {'form':form}
    return render(request,'FeedApp/profile.html',context)

@login_required
def myfeed(request):    
    comment_count_list = []
    like_count_list = []
    posts = Post.objects.filter(username=request.user).order_by('-date_posted') #username is a field of Post
    