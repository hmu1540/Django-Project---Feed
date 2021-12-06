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
    for p in posts:
        c_count = Comment.objects.filter(post=p).count()
        l_count = Like.objects.filter(post=p).count()
        comment_count_list.append(c_count)
        like_count_list.append(l_count)
    zipped_list = zip(posts, comment_count_list, like_count_list)    #pass post,comment count,like count to context or zip all up so that they are arranged in a 'dataframe' way
    
    context = {'posts':posts, 'zipped_list':zipped_list}
    return render(request, 'FeedApp/myfeed.html', context)



@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
    else:
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.username = request.user
            new_post.save()
            return redirect('FeedApp:myfeed')

    context= {'form':form}
    return render(request, 'FeedApp/new_post.html', context) 



@login_required
def comments(request, post_id):
    if request == 'POST' and request.POST.get('btn1'):
        text = request.POST.get("comment")
        Comment.objects.create(post_id=post_id,username=request.user,text=text,date_added=date.today())

    comments = Comment.objects.filter(post=post_id)
    post = Post.objects.get(id=post_id)

    context ={'comments':comments, 'post':post}

    return render(request, 'FeedApp/comments.html', context)

@login_required
def friendsfeed(request):    
    comment_count_list = []
    like_count_list = []
    posts = Post.objects.filter(username=request.user).order_by('-date_posted') #username is a field of Post
    for p in posts:
        c_count = Comment.objects.filter(post=p).count()
        l_count = Like.objects.filter(post=p).count()
        comment_count_list.append(c_count)
        like_count_list.append(l_count)
    zipped_list = zip(posts, comment_count_list, like_count_list)    #pass post,comment count,like count to context or zip all up so that they are arranged in a 'dataframe' way
    
    if request.method == 'POST' and request.POST.get('like'):
        post_to_like = request.POST.get('like')
        print(post_to_like)
        like_already_exists = Like.objects.filter(post_id=post_to_like,username=request.user)
        if not like_already_exists:
            Like.objects.create(post_id=post_to_like,username=request.user)
            return redirect('FeedApp:friendsfeed')


    context = {'posts':posts, 'zipped_list':zipped_list}
    return render(request, 'FeedApp/myfeed.html', context)
