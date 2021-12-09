from django.db.models.fields import related
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
    """ The home page for FeedApp. """
    return render(request, 'FeedApp/index.html')



@login_required #only after logging in, can access the profile funciton(protection)
def profile(request):
    profile = Profile.objects.filter(user=request.user) # only user that logged on can access information of their own.
    if not profile.exists():
        Profile.objects.create(user=request.user)
    profile = Profile.objects.get(user=request.user) # can use get() only when we are sure the user exists

    if request.method != 'POST':
        form = ProfileForm(instance=profile) 
    else:
        form = ProfileForm(instance=profile,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('FeedApp:index')
        
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
    if request.method == 'POST' and request.POST.get('btn1'):
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
    friends = Profile.objects.filter(user=request.user).values('friends')
    posts = Post.objects.filter(username__in=friends).order_by('-date_posted') #username is a field of Post
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
    return render(request, 'FeedApp/friendsfeed.html', context)

@login_required
def friends(request):
    # get the admin_profile and user prof to create the first relationship
    # admin_profile = Profile.objects.get(user=1)
    user_profile = Profile.objects.get(user=request.user)

    # to get My Friends
    user_friends = user_profile.friends.all()
    user_friends_profiles = Profile.objects.filter(user__in=user_friends)

    # to get Friends requsest snet
    user_relationships = Relationship.objects.filter(sender=user_profile)
    request_sent_profiles = user_relationships.values('receiver')

    # to get eligibile profiles -exlcue the user, their existing friend, and friend request sent already
    all_profiles = Profile.objects.exclude(user=request.user).exclude(id__in=user_friends_profiles).exclude(id__in=request_sent_profiles)

    # to get friend questt receive by the user
    request_received_profiles = Relationship.objects.filter(receiver=user_profile,status='sent')

    # if this is the 1st time to acesss the friend requests page, ccreate the first relationship
    # with the admin of the website(so the admin is the friends with everyone)

    # if not user_relationships.exists(): # 'filter' works with exists 'get' does not
    #     Relationship.objects.create(sender=user_profile,receiver=admin_profile,status='sent')

    # check to see WICH submit button was pressed(sending a friend reques or accep t afrind request)

    # this is to process all send request
    if request.method == 'POST' and request.POST.get('send_requests'):
        receivers = request.POST.getlist('send_requests')
        for receiver in receivers:
            receiver_profile = Profile.objects.get(id=receiver)
            Relationship.objects.create(sender=user_profile, receiver=receiver_profile,status='sent')
        return redirect('FeedApp:friends')

    # this is to process all receive request
    if request.method == 'POST' and request.POST.get('receive_requests'):
        senders = request.POST.getlist('receive_requests')
        for sender in senders:
            # updatae the realtinohsp model for the sender to status accepted
            Relationship.objects.filter(id=sender).update(status='accepted')

            # createa n realtinsoh ponject ot access the sender user id
            #  to add to the freinds list of teh suer
            relationship_obj = Relationship.objects.get(id=sender)
            user_profile.friends.add(relationship_obj.sender.user)

            # add teh user to the friends list of the sender profile
            relationship_obj.sender.friends.add(request.user)

    context = {'user_friends_profiles':user_friends_profiles, 'user_relationships':user_relationships,
    'all_profiles':all_profiles,'request_received_profiles':request_received_profiles}

    return render(request, 'FeedApp/friends.html', context)