from django.shortcuts import render, redirect,get_object_or_404
from luxverth.models import user_details as user_table
from luxverth.models import Post as post_table
from luxverth.models import Comment as comment_table
from luxverth.models import Reply as reply_table
from .models import Chats as Chat, text_Message as Message
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
#from luxverth.models import SharedPost as Shared_table
from luxverth.models import Notification as Notification_table
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .form import SignUpForm
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from django.http import JsonResponse,HttpResponseRedirect
import mimetypes
from django.db.models import Q
from django.db.models import F
from django.contrib import messages
from .models import *
from datetime import datetime
# Create your views here.
def newsfeed_view(request):
    if request.user.is_authenticated is False:
        return redirect('login')
        
    ctx = {}
    if request.GET.get("q"):
        url_parameter = request.GET.get("q")
        var_type = request.GET.get("type")
        if url_parameter:
            artists = user_table.objects.filter(name__icontains=url_parameter)
        else:
            artists = user_table.objects.all()

        ctx["artists"] = artists
        if request.is_ajax():
            if var_type == 'chat-search':
                html = render_to_string(
                    template_name="chat_search.html", context={"artists": artists}
                )
                data_dict = {"html_from_view": html,"type":'2'}
            elif var_type == 'chat-group-search':
                artists = Group.objects.filter(group_name__icontains=url_parameter)
                html = render_to_string(
                    template_name="chat_group_search.html", context={"artists": artists}
                )
                data_dict = {"html_from_view": html,"type":'3'}
            else:
                html = render_to_string(
                template_name="search_result.html", context={"artists": artists}
                )
                data_dict = {"html_from_view": html,"type":''}
            return JsonResponse(data=data_dict, safe=False)
    user_profile = user_table.objects.get(user=request.user)
    posts = []
    post_date = []
    admin = user_table.objects.get(user__username = 'admin')
    feelings = Feeling.objects.all()
    now = datetime.now()
    try:
        print('test')
        mood = Mood.objects.get(user=request.user, date=now.strftime("%Y-%m-%d 00:00:00"))
        modal = 'nope'
        print('test2')
    except:
        if request.user.is_authenticated is True:
            print
            modal = 'popup'
        else:
            modal = 'nope'
    for following in user_profile.followings.all():
        for post in following.user_details.post.all().order_by('created_on'):
            
            post_date.append(post.created_on)
            posts.append(post)
    for post in user_profile.post.all().order_by('-created_on'):
        if post in posts:
            continue
        post_date.append(post.created_on)
        posts.append(post)
    for post in admin.post.all():
        if post in posts:
            continue
        post_date.append(post.created_on)
        posts.append(post)
    p = []
    posts = [x for _, x in sorted(zip(post_date, posts))]
    posts.reverse()
    page = request.GET.get('page', 1)
    paginator = Paginator(posts, 1)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    
    news_posts = admin.post.all().order_by('-id')[:6]

    context = {
        'user_profile':user_profile,
        'page':'newsfeed',
        'posts':posts,
        'count':7,
        'count2':3,
        'news_posts':news_posts,
        'modal':modal,
        'feelings':feelings,
        
    }
    return render(request,'main.html',context)

def login_view(request):
    form = SignUpForm()
    login_form = AuthenticationForm()
    error = None
    signup = 'hide'
    log_in =''
    signup_tab=''
    login_tab='active'
    if request.method == 'POST':
        print("tets")
        if 'signup' in request.POST:
            signup = ''
            log_in ='hide'
            signup_tab='active'
            login_tab=''
            form = SignUpForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                user_profile = user_table(
                    user = request.user,
                    name = request.user.username,
                )
                user_profile.save()
                
                return redirect('newsfeed')
        elif 'login' in request.POST:
             signup = 'hide'
             log_in =''
             signup_tab=''
             login_tab='active'
             print("loggin in")
             login_form = AuthenticationForm(request=request, data=request.POST)
             if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('newsfeed')
                else:
                    error = "Invalid username or password."
             else:
                 error = "Invalid username or password."
    return render(request, 'login.html', {'form': form,'login_form':login_form,'error':error,'signup':signup,'signup_tab':signup_tab,
    'login':log_in,'login_tab':login_tab})

def signupView(request):
    form = SignUpForm()
    login_form = AuthenticationForm()
    error = None
    signup = 'hide'
    log_in =''
    signup_tab=''
    login_tab='active'
    if request.method == 'POST':
        print("tets")

        if 'signup' in request.POST:
            signup = ''
            log_in ='hide'
            signup_tab='active'
            login_tab=''
            form = SignUpForm(request.POST)
            email = request.POST.get('email')
            try:
                print(email)
                user = User.objects.get(email=email)
                error = 'email alreay exists.'
                print(error)
                e = True
            except:
                e = False
                pass
            if form.is_valid() and e == False:
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                user_profile = user_table(
                    user = request.user,
                    name = request.user.username,
                )
                user_profile.save()
                
                return redirect('newsfeed')
        elif 'login' in request.POST:
             signup = 'hide'
             log_in =''
             signup_tab=''
             login_tab='active'
             print("loggin in")
             login_form = AuthenticationForm(request=request, data=request.POST)
             if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('newsfeed')
                else:
                    error = "Invalid username or password."
             else:
                 error = "Invalid username or password."
    return render(request, 'signup.html', {'form': form,'login_form':login_form,'error':error,'signup':signup,'signup_tab':signup_tab,
    'login':log_in,'login_tab':login_tab})


def logout_view(request):
    logout(request)
    return redirect('/login/')

def profile_view(request,user):
    if request.user.is_authenticated is False:
        return redirect('login')
    user = User.objects.get(username=user)
    user_profile = user_table.objects.get(user=user)
    context = {
        'user_profile':user_profile,
        'page':'profile',
        'posts':user_profile.post.all,
        'count':3,
        'count2':2
    }
    return render(request,'main.html',context)
def post(request):
    if request.user.is_authenticated is False:
        return redirect('login')
    try:
        if request.method == 'POST' and request.FILES['myfile']:
            print("tests")
            myfile = request.FILES['myfile']
            file_mime = mimetypes.guess_type(myfile.name)
            print(file_mime)
            if file_mime[0] == 'image/jpeg' :
                post_type = 'photo'
            elif file_mime[0] == 'image/png' :
                post_type = 'photo'
            elif file_mime[0] == 'video/mp4':
                post_type = 'video'
            else:
                message = 'file type is not accepted'
                print("file type is not accepted")
                return redirect('newsfeed')
            fs = FileSystemStorage('luxverth/static/img/posts/')
            filename = fs.save(myfile.name, myfile)
            image = 'img/posts/'+myfile.name
    except:
        post_type = 'text'
        image = 'None'
    post = post_table(
        user = request.user,
        image = image,
        caption = request.POST['caption'],
        desc = request.POST['desc'],
        post_type = post_type
    )
    post.save()
    request.user.user_details.post.add(post)
        
    return redirect('newsfeed')
def sharePost(request):
    if request.user.is_authenticated is False:
        return redirect('login')
    post = post_table.objects.get(id=request.POST.get('post_id'))
    sharepost = post_table(
        user = request.user,
        image = post.image,
        caption = request.POST.get('caption'),
        desc = request.POST.get('desc'),
        SharedPost = True,
        sharedpost_user = post.user,
        sharedpost_caption = post.caption,
        sharedpost_desc = post.desc,
        o_post = post.id,
        post_type = post.post_type
    )
    sharepost.save()
    if request.user != post.user:
            notification = Notification_table(
                user = request.user,
                notify_type = 'shared your post',
                notify_post = sharepost,
            )
            notification.save()
            post.user.user_details.notifications.add(notification)
            post.user.user_details.notification_bell = True
            post.user.user_details.save()
    request.user.user_details.post.add(sharepost)
    return redirect('/profile/'+request.user.username)

def follow(request,user_id):
    if request.user.is_authenticated is False:
        return redirect('login')
    user = User.objects.get(id=user_id)
    if user in request.user.user_details.followings.all():
        request.user.user_details.followings.remove(user)
        request.user.user_details.following_count = request.user.user_details.following_count - 1
        user.user_details.followers.remove(request.user)
        worth = 0
        #if user in request.user.user_details.followers.all():
        #    worth = user.user_details.worth * (0.5/100)
        worth = (request.user.user_details.worth + worth) * (0.5/100) 
        user.user_details.worth = user.user_details.worth - worth
        decrease_worth(request,user,worth)
        user.user_details.follower_count = user.user_details.follower_count - 1
        notification = Notification_table.objects.filter(
                    user = request.user,
                    notify_user_request=user,
                )
        notification.delete()
    else:
        if user.user_details.privacy == False:
            request.user.user_details.followings.add(user)
            request.user.user_details.following_count = request.user.user_details.following_count + 1
            worth = 0
            #if user in request.user.user_details.followers.all():
            #    worth = user.user_details.worth * (0.5/100)
            worth = (request.user.user_details.worth -worth) * (0.5/100) 
            user.user_details.worth = user.user_details.worth + worth
            increase_worth(request,user,worth)
            user.user_details.followers.add(request.user)
            user.user_details.follower_count = user.user_details.follower_count + 1
            notification = Notification_table(
                user = request.user,
                notify_type='Started following you',
                notify_user_request=user,
            )
            notification.save()
            user.user_details.notifications.add(notification)
            user.user_details.notification_bell = True
            user.user_details.save()
            print(user.user_details.notification_bell)
        else:
            if request.user in user.user_details.follow_requests.all():
                user.user_details.follow_requests.remove(request.user)
                notification = Notification_table.objects.get(
                    user = request.user,
                    notify_type='Requested to follow You',
                    notify_user_request=user,
                )
                notification.delete()
                user.user_details.save()
            else:
                user.user_details.follow_requests.add(request.user)
                notification = Notification_table(
                    user = request.user,
                    notify_type='Requested to follow You',
                    notify_user_request=user,
                )
                notification.save()
                user.user_details.notifications.add(notification)
                user.user_details.notification_bell = True
                user.user_details.save()

    user.user_details.save()
    request.user.user_details.save()
    data={
        'following_count':request.user.user_details.following_count,
        'follower_count':user.user_details.follower_count
    }
    return JsonResponse(data)
def follow_request(request,user_id):
    if request.user.is_authenticated is False:
        return redirect('login')
    user = User.objects.get(id=user_id)
    if user in request.user.user_details.follow_requests.all():
            request.user.user_details.followers.add(user)
            request.user.user_details.follow_requests.remove(user)
            request.user.user_details.follower_count = request.user.user_details.follower_count + 1
            worth = 0
            #if request.user in user.user_details.followers.all():
            #    worth = request.user.user_details.worth * (0.5/100)
            worth = (user.user_details.worth -worth) * (0.5/100) 
            request.user.user_details.worth = user.user_details.worth + worth
            increase_worth(request,request.user,worth)
            user.user_details.followings.add(request.user)
            user.user_details.following_count = user.user_details.following_count + 1
    elif user in request.user.user_details.followers.all():
            request.user.user_details.followers.remove(user)
            request.user.user_details.follower_count = request.user.user_details.follower_count - 1
            user.user_details.followings.remove(request.user)
            worth = 0
            #if request.user in user.user_details.followers.all():
            #    worth = request.user.user_details.worth * (0.5/100)
            worth = (user.user_details.worth -worth) * (0.5/100) 
            request.user.user_details.worth = request.user.user_details.worth - worth
            decrease_worth(request,request.user,worth)
            user.user_details.following_count = request.user.user_details.following_count - 1
    user.user_details.save()
    request.user.user_details.save()
    data={
        'following_count':request.user.user_details.following_count,
        'follower_count':user.user_details.follower_count
    }
    return JsonResponse(data)

def like_no(user,post):
    if user.is_authenticated is False:
        return redirect('login')
    
    if user in post.liker_users.all():
        post.liker_users.remove(user)
        post.like_count = post.like_count - 1
        if user != post.user:
            Notification = Notification_table.objects.get(user=user,notify_type='liked your post',notify_post=post)
            Notification.delete()
            
    else:
        post.liker_users.add(user)
        post.like_count = post.like_count + 1
        if user != post.user:
            notification = Notification_table(
                user = user,
                notify_type = 'liked your post',
                notify_post = post,
            )
            notification.save()
            post.user.user_details.notifications.add(notification)
            post.user.user_details.notification_bell = True
            post.user.user_details.save()
            
    post.save()
    return post.like_count
def comment_no(comment,post):
    if comment.user.is_authenticated is False:
        return redirect('login')
    post.comments.add(comment)
    post.comment_count = post.comment_count + 1
    if comment.user != post.user:
            notification = Notification_table(
                user = comment.user,
                notify_type = 'commented on your post',
                notify_post = post,
                notify_comment = comment
            )
            notification.save()
            post.user.user_details.notifications.add(notification)
            post.user.user_details.notification_bell = True
            post.user.user_details.save()
    post.save()
    return post.comment_count
def reply_no(reply,post,comment):
    if reply.user.is_authenticated is False:
        return redirect('login')
    comment.replies.add(reply)
    comment.save()
    post.comment_count = post.comment_count + 1
    if reply.user != post.user:
            notification = Notification_table(
                user =reply.user,
                notify_type = 'replied  on your post',
                notify_post = post,
                notify_comment = comment,
                notify_reply = reply
            )
            notification.save()
            post.user.user_details.notifications.add(notification)
            post.user.user_details.notification_bell = True
            post.user.user_details.save()
    if reply.user != comment.user:
            notification = Notification_table(
                user = reply.user,
                notify_type = 'replied to your comment',
                notify_post = post,
                notify_comment = comment,
                notify_reply = reply
            )
            notification.save()
            comment.user.user_details.notifications.add(notification)
            comment.user.user_details.notification_bell = True
            comment.user.user_details.save()
    post.save()
    return post.comment_count

def liker_avatars(request,post_id):
    if request.user.is_authenticated is False:
        return redirect('login')
    post = post_table.objects.get(id=post_id)
    return render(request,'liker-avatars.html',{'post':post})
def likers(request,post_id):
    if request.user.is_authenticated is False:
        return redirect('login')
    post = post_table.objects.get(id=post_id)
    return render(request,'likers.html',{'post':post})
def comments(request,post_id,count,count2):
    if request.user.is_authenticated is False:
        return redirect('login')
    post = post_table.objects.get(id=post_id)
    return render(request,'comments.html',{'post':post,'count':count,'count2':count2})

def change_image(request):
    if request.user.is_authenticated is False:
        return redirect('login')
    print("change")
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage('luxverth/static/img/profile/')
        filename = fs.save(myfile.name, myfile)
        user_profile = user_table.objects.get(user=request.user)
        print(request.POST.get('id'))
        if request.POST.get('id') == '0':
            user_profile.profile_image = 'img/profile/'+myfile.name
        elif request.POST.get('id') == '1':
            user_profile.fav_image1 = 'img/profile/'+myfile.name
        elif request.POST.get('id') == '2':
            user_profile.fav_image2 = 'img/profile/'+myfile.name
        elif request.POST.get('id') == '3':
            user_profile.fav_image3 = 'img/profile/'+myfile.name
        elif request.POST.get('id') == '4':
            user_profile.fav_image4 = 'img/profile/'+myfile.name
        user_profile.save()
    return redirect('newsfeed')

def change_group_image(request):
    print("change")
    if request.method == 'POST' and request.FILES['myfile']:
        profile_image = request.FILES['myfile']
        group = Group.objects.get(id=request.POST.get('id'))
        group.image = profile_image
        group.save()
        url='/messenger/'+request.POST.get('id')+'?t=group'
        return redirect(url)

def notepadView(request):
    print('test')
    if request.method == 'POST':
        if 'create' in request.POST:
            note = Notepad(
                user=request.user,
                title=request.POST.get('title'),
                content=request.POST.get('content')
            )
            note.save()
            return HttpResponseRedirect('/notepad')
        elif 'edit' in request.POST:
            note = Notepad.objects.get(id=request.POST.get('id'))
            note.title=request.POST.get('title')
            note.content=request.POST.get('content')
            note.save()
            print('yaasd')
            return HttpResponseRedirect('/notepad')
    print('teasd')
    user_profile = user_table.objects.get(user = request.user)
    notes = Notepad.objects.filter(user=request.user)
    return render(request,'main.html',{'user_profile':user_profile,
        'page':'notepad','notes':notes})
    
def comment_like(request):
    if request.user.is_authenticated is False:
        return redirect('login')
    print('comment')
    post_id = request.GET.get('post_id')
    post = post_table.objects.get(id=post_id)
    if request.GET.get('like_on') == 'comment':
        print('comment')
        comment_id = request.GET.get('comment_id')
        print(comment_id)
        comment = comment_table.objects.get(id=comment_id)
        if request.user in comment.comment_likers.all():
            if request.user != comment.user:
                Notification = Notification_table.objects.get(user=request.user,notify_type='liked your reply',notify_comment=comment)
                Notification.delete()
            comment.comment_likers.remove(request.user)
            comment.like_count = comment.like_count - 1
            like_count = comment.like_count
            
        else:
            comment.comment_likers.add(request.user)
            comment.like_count = comment.like_count + 1
            like_count = comment.like_count
            if request.user != comment.user:
                notification = Notification_table(
                    user = request.user,
                    notify_type = 'liked your comment',
                    notify_post = post,
                    notify_comment = comment
                )
                notification.save()
                comment.user.user_details.notifications.add(notification)
                comment.user.user_details.notification_bell = True
                comment.user.user_details.save()
        comment.save()
    else:
        comment_id = request.GET.get('reply_id')
        comment = reply_table.objects.get(id=comment_id)
        if request.user in comment.reply_likers.all():
            if request.user != comment.user:
                Notification = Notification_table.objects.get(user=request.user,notify_type='liked your reply',notify_reply=comment)
                Notification.delete()
            comment.reply_likers.remove(request.user)
            comment.like_count = comment.like_count - 1
            like_count = comment.like_count
            
        else:
            comment.reply_likers.add(request.user)
            comment.like_count = comment.like_count + 1
            like_count = comment.like_count
            if request.user != comment.user:
                notification = Notification_table(
                    user = request.user,
                    notify_type = 'liked your reply',
                    notify_post = post,
                    notify_reply = comment
                )
                notification.save()
                comment.user.user_details.notifications.add(notification)
                comment.user.user_details.notification_bell = True
                comment.user.user_details.save()
        comment.save()
    data={
        'like_count':like_count
    }
    return JsonResponse(data)

def delete(request):
    if request.user.is_authenticated is False:
        return redirect('login')
    id = request.GET.get('id')
    post_id = request.GET.get('post_id')
    print(post_id)
    post = post_table.objects.get(id=post_id)
    if request.GET.get('delete_t') == 'post':
        post_table.objects.get(id=id).delete()
        try:
            post_table.objects.get(o_post=id).delete()
        except:
            pass
        return JsonResponse({})
    elif request.GET.get('delete_t') == 'comment':
        comment = comment_table.objects.get(id=id)
        count = comment.replies.all().count()
        comment.delete()
        post.comment_count = post.comment_count - 1 - count
        post.save()
        count = post.comment_count
        
    elif request.GET.get('delete_t') == 'reply':
        reply_table.objects.get(id=id).delete()
        post.comment_count = post.comment_count - 1 
        post.save()
        count = post.comment_count
    return JsonResponse(data={'count':count})
    

def pin_post(request):
    if request.user.is_authenticated is False:
        return redirect('login')
    post_id = request.GET.get('post_id')
    post = post_table.objects.get(id=post_id)
    if post in request.user.user_details.pinned.all():
        request.user.user_details.pinned.remove(post)
        text = 'pin'
    else:
        request.user.user_details.pinned.add(post)
        text = 'un pin'
    return JsonResponse({'text':text})

def notification_bell(request):
    if request.user.is_authenticated is False:
        return redirect('login')
    request.user.user_details.notification_bell = False
    request.user.user_details.save()
    return JsonResponse({})

def post_view(request,post_id):
    if request.user.is_authenticated is False:
        return redirect('login')
    post = post_table.objects.get(id=post_id)
    user_profile = user_table.objects.get(user = request.user)
    return render(request,'main.html',{'user_profile':user_profile,
        'page':'single_post',
        'post':post,
        'count':7,
        'count2':3})
def followers_view(request,user):
    if request.user.is_authenticated is False:
        return redirect('login')
    user = User.objects.get(username=user)
    user_profile = user_table.objects.get(user = user)
    return render(request,'main.html',{'user_profile':user_profile,
        'page':'people',
        'people':user_profile.followers.all(),
        'count':3,
        'count2':2})

def follower_request_view(request):
    if request.user.is_authenticated is False:
        return redirect('login')
    user_profile = user_table.objects.get(user = request.user)
    return render(request,'main.html',{'user_profile':user_profile,
        'page':'follow_requests',
        'people':user_profile.follow_requests.all(),
        'count':3,
        'count2':2})

def followings_view(request,user):
    if request.user.is_authenticated is False:
        return redirect('login')
    user = User.objects.get(username=user)
    user_profile = user_table.objects.get(user = user)
    return render(request,'main.html',{'user_profile':user_profile,
        'page':'people',
        'people':user_profile.followings.all(),
        'count':3,
        'count2':2})
def follow_btn_view(request,user_id):
    if request.user.is_authenticated is False:
        return redirect('login')
    user = User.objects.get(id=user_id)
    print(user)
    return render(request,'follow_btn.html',{'person':user})

def follow_req_btn_view(request,user_id):
    if request.user.is_authenticated is False:
        return redirect('login')
    user = User.objects.get(id=user_id)
    print(user)
    return render(request,'follow_req_btn.html',{'person':user})

def posts_view(request,user):
    if request.user.is_authenticated is False:
        return redirect('login')
    user = User.objects.get(username=user)
    user_profile = user_table.objects.get(user=user)
    posts=[]
    for post in user_profile.post.all():
        if post.SharedPost == False:
            if post.post_type == 'photo':
                print(post.id)
                posts.append(post)
            elif post.post_type == 'text':
                posts.append(post)
        
    context = {
        'user_profile':user_profile,
        'page':'posts',
        'header':'posts',
        'posts':posts,
        'count':7,
        'count2':3
    }
    return render(request,'main.html',context)
def sharedposts_view(request,user):
    if request.user.is_authenticated is False:
        return redirect('login')
    user = User.objects.get(username=user)
    user_profile = user_table.objects.get(user=user)
    posts=[]
    for post in user_profile.post.all():
        if post.SharedPost == True:
            posts.append(post)
        
    context = {
        'user_profile':user_profile,
        'page':'posts',
        'header':'sharedposts',
        'posts':posts,
        'count':7,
        'count2':3
    }
    return render(request,'main.html',context)

def videos_view(request,user):
    if request.user.is_authenticated is False:
        return redirect('login')
    user = User.objects.get(username=user)
    user_profile = user_table.objects.get(user=user)
    posts=[]
    for post in user_profile.post.all():
        if post.SharedPost == False:
            if post.post_type == 'video':
                posts.append(post)
        
    context = {
        'user_profile':user_profile,
        'page':'posts',
        'header':'videos',
        'posts':posts,
        'count':7,
        'count2':3
    }
    return render(request,'main.html',context)

def pinnedposts_view(request):
    if request.user.is_authenticated is False:
        return redirect('login')
    user_profile = user_table.objects.get(user=request.user)
    posts=[]
    for post in user_profile.pinned.all():
        posts.append(post)
        
    context = {
        'user_profile':user_profile,
        'page':'posts',
        'header':'pinnedposts',
        'posts':posts,
        'count':7,
        'count2':3
    }
    return render(request,'main.html',context)

def edit_profile_view(request):
    user_profile = user_table.objects.get(user=request.user)
    if request.method == 'POST':
        user_profile.name = request.POST.get('name')
        user_profile.country = request.POST.get('country')
        user_profile.city = request.POST.get('city')
        user_profile.description = request.POST.get('description')
        user_profile.phone_no = request.POST.get('phone_no')
        user_profile.gender = request.POST.get('gender')
        user_profile.save()
    context = {
        'user_profile':user_profile,
        'page':'edit-profile',
        'count':3,
    }
    return render(request,'main.html',context)

def privacy_view(request):
    user_profile = user_table.objects.get(user=request.user)
    if request.method == 'POST':
        if request.POST.get('privacy') == 'on':
            user_profile.privacy = True
            user_profile.save()
        else:
            user_profile.privacy = False
            user_profile.save()
    context = {
        'user_profile':user_profile,
        'page':'privacy',
        'count':3,
    }
    return render(request,'main.html',context)
def change_pass_view(request):
    user_profile = user_table.objects.get(user=request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            form = PasswordChangeForm(request.user)
            return render(request, 'main.html', {
                'form': form,
                'user_profile':user_profile,
                'page':'change_pass',
            })
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'main.html', {
        'form': form,
        'user_profile':user_profile,
        'page':'change_pass',
    })

def increase_worth(request,user,worth):
    for user in user.user_details.followings.all():
        if user == request.user:
            pass
        elif user in request.user.user_details.followings.all():
            pass
        worth = worth * (0.5/100)
        if worth < 0.0001:
            return
        user.user_details.worth = user.user_details.worth
        user.user_details.save()
        increase_worth(request,user,worth)
    return
def decrease_worth(request,user,worth):
    for user in user.user_details.followings.all():
        if user == request.user:
            pass
        elif user in request.user.user_details.followings.all():
            pass
        worth = worth * (0.5/100)
        if worth < 0.0001:
            return
        user.user_details.worth = user.user_details.worth
        user.user_details.save()
        decrease_worth(request,user,worth)
    return

def messenger_view(request,user=None):
    if request.user.is_authenticated is False:
        return redirect('login')
    chat_list = Chat.objects.order_by('-last_text_message__timestamp').filter(Q(user1=request.user) | Q(user2=request.user))
    group_list = Group.objects.filter(members__in=[request.user.id])
    chats = []
    for chat in chat_list:
        if chat.user1 == request.user:
            if chat.u1_clear_chat != chat.last_text_message:
                chats.append(chat)
        else:
            if chat.u2_clear_chat != chat.last_text_message:
                chats.append(chat)
    chat_list = chats
    if user == None:
        return render(request,'messanger.html',{'page':'inbox','chat_list':chat_list,'group_list':group_list})
    if request.GET.get('t') == 'group':
        group = Group.objects.get(id=user)
        if request.user not in group.members.all():
            group.members.add(request.user)
            group.save()
        
        return render(request,'messanger.html',{'t':'group','page':'messenger','group':group,'chat_list':chat_list,'group_list':group_list,'chat_id':group})
    messages = get_last_messages(request,user,5)
    user_profile = user_table.objects.get(user__username=user)
    user = User.objects.get(username=user)
    chat_id = get_current_chat(user,request.user)
    
    return render(request,'messanger.html',{'page':'messenger','messages':messages,'user_profile':user_profile,'chat_list':chat_list,'chat_id':chat_id,'count':5,'group_list':group_list})
def load_messages(request,user,count):
    messages = get_last_messages(request,user,count+5)
    
    user_profile = user_table.objects.get(user__username=user)
    data = {
            'count':count+5,
            'messages':messages,
            'user_profile':user_profile
        }
    return render(request,'load_messages.html',data)
def get_last_messages(request,user,count):
    if request.user.is_authenticated is False:
        return redirect('login')
    if user == request.user:
        return redirect('inbox')
    user = User.objects.get(username=user)
    try:
        chat = Chat.objects.get(user1=user,user2=request.user)
        if chat.u2_status == 'unread' and request.user.user_details.message_notification_count > 0 :
            request.user.user_details.message_notification_count = request.user.user_details.message_notification_count - 1
            request.user.user_details.save()
        print(chat.user2)
        print("read status")
        chat.u2_status = 'read'
        last_delete_chat= chat.u2_clear_chat
        chat.save()
    except:
        try:
            chat = Chat.objects.get(user1=request.user,user2=user)
            if chat.u1_status == 'unread' and request.user.user_details.message_notification_count > 0 :
                print("test noti "+chat.u1_status)
                request.user.user_details.message_notification_count = request.user.user_details.message_notification_count - 1
                request.user.user_details.save()
            print(chat.user1)
            print(chat.user2)
            print("before read status:"+chat.u1_status)
            chat.u1_status = 'read'
            print("after read status:"+chat.u1_status)
            last_delete_chat= chat.u1_clear_chat
            chat.save()
        except:
            chat = Chat(
                user1 = user,
                user2 = request.user
            )
            chat.save()
    count = int(count) + 1
    if last_delete_chat ==None:
        return chat.messages.order_by('-timestamp').all()[:count]
    else:
        print(count)
        
        return chat.messages.filter(id__gt=last_delete_chat.id).order_by('-timestamp')[:count]
    

def get_user_contact(username):
    user = get_object_or_404(User, username=username)
    return get_object_or_404(Contact, user=user)


def get_current_chat(user1,user2):
    try:
        chat = Chat.objects.get(user1=user1,user2=user2)
    except:
        chat = Chat.objects.get(user1=user2,user2=user1)
    
    return get_object_or_404(Chat, id=chat.id)

def clear_chat(request,chat_id):
    chat = Chat.objects.get(id=chat_id)
    if chat.user1 == request.user:
        chat.u1_clear_chat = chat.last_text_message
        user = chat.user2
    else:
        chat.u2_clear_chat = chat.last_text_message
        user = chat.user1
    chat.save()
    return messenger_view(request,user)

def leaderboard_view(request):
    if request.user.is_authenticated is False:
        return redirect('login')
    user_profile = user_table.objects.get(user=request.user)
    peoples = user_table.objects.order_by('-worth').all()
    print(peoples[1])
    context = {
        'user_profile':user_profile,
        'page':'leaderboard',
        'peoples':peoples,
    }
    return render(request,'main.html',context)

def createGroupView(request):
    if request.method == 'POST':
        group = Group(
            group_name = request.POST.get('name'),
            description = request.POST.get('description'),
            group_admin = request.user
        )
        group.save()
        group.members.add(request.user)
        group.save()
        url = '/messenger/'+str(group.id)+'?t=group'
        return redirect(url)
    return render(request,'messenger',{})

def moodCaptureView(request):
    now = datetime.now()
    if request.method == 'POST':
        mood = Mood(
            user = request.user,
            date = now.strftime("%Y-%m-%d"),
            date2 = now.strftime("%Y-%m-%d"),
            mood = request.POST.get('mood'),
        )
        mood.save()
        #feelings= Feeling.objects.all()
        feelings0 = request.POST.getlist('feelings')
        print(feelings0)
        for f in feelings0:
            print(f)
            feeling = Feeling.objects.get(feeling=f)
            mood.feelings.add(feeling)
        mood.save()
    return HttpResponseRedirect('/newsfeed')

def getMoodView(request):
    d = request.GET.get('date')
    print(d)
    moods = Mood.objects.filter(user=request.user)
    mood='not set yet'
    feelings = []
    for m in moods:
        if m.date.strftime("%B %d, %Y") == d:
            mood = m.mood
            for f in m.feelings.all():
                feelings.append(f.feeling)
    data={
        'mood':mood,
        'feelings':feelings,
    }

    return JsonResponse(data,safe=False)

def calenderView(request):
    user_profile = user_table.objects.get(user=request.user)
    context = {
        'user_profile':user_profile,
        'page':'calendar',
    }
    return render(request,'main.html',context)