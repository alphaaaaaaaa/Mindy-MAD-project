from django.db import models
from django.contrib.auth.models import User

# Create your models here.



class Reply(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    reply_text = models.TextField()
    reply_likers = models.ManyToManyField(User,related_name='reply_likers',default=None)
    like_count = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE) 
    comment_text = models.TextField()
    comment_likers = models.ManyToManyField(User,related_name='comment_likers',default=None)
    like_count = models.IntegerField(default=0)
    replies = models.ManyToManyField(Reply,related_name='replies',default=None)
    created_on = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='post_user')
    image = models.TextField()
    caption = models.TextField()
    like_count = models.IntegerField(default=0)
    desc = models.TextField(default='test')
    comments = models.ManyToManyField(Comment,related_name='comments')
    comment_count = models.IntegerField(default=0)
    shared_post_count = models.IntegerField(default=0)
    SharedPost = models.BooleanField(default=False)
    sharedpost_user = models.ForeignKey(User,on_delete=models.CASCADE,default=None,null=True,related_name='shared_post_user')
    sharedpost_caption = models.TextField(default='none')
    sharedpost_desc = models.TextField(default='none')
    o_post = models.IntegerField(default=0)
    post_type = models.CharField(max_length=20,default='photo')
    created_on = models.DateTimeField(auto_now_add=True)
    liker_users = models.ManyToManyField(User,related_name='likers',default=None,null=True,blank=True)



class text_Message(models.Model):
    user = models.ForeignKey(
        User, related_name='char', on_delete=models.CASCADE,default=None,blank=True,null=True)
    content = models.TextField(default="asd")
    timestamp = models.DateTimeField(auto_now_add=True)

class Group(models.Model):
    group_name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(default='/default-avatar.png')
    group_admin = models.ForeignKey(User, on_delete=models.PROTECT,related_name="group_admin")
    members = models.ManyToManyField(User,related_name="group_members")
    messages = models.ManyToManyField(text_Message,related_name='group_messages', blank=True)
    last_text_message = models.ForeignKey(text_Message,on_delete=models.CASCADE,related_name='group_last_message',default=None,blank=True,null=True)

    def __str__(self):
        return self.group_name

class Chats(models.Model):
    user1 = models.ForeignKey(User,related_name='user1',on_delete=models.CASCADE,default=None,blank=True,null=True)
    user2 = models.ForeignKey(User,related_name='user2',on_delete=models.CASCADE,default=None,blank=True,null=True)
    messages = models.ManyToManyField(text_Message,related_name='messages', blank=True)
    last_text_message = models.ForeignKey(text_Message,on_delete=models.CASCADE,related_name='last_message',default=None,blank=True,null=True)
    u1_status = models.CharField(max_length=10,default='unread')
    u2_status = models.CharField(max_length=10,default='unread')
    u1_clear_chat = models.ForeignKey(text_Message,on_delete=models.CASCADE,related_name='u1_last_delete_message',default=None,blank=True,null=True)
    u2_clear_chat = models.ForeignKey(text_Message,on_delete=models.CASCADE,related_name='u2_last_delete_message',default=None,blank=True,null=True)
    def __str__(self):
        return "{}".format(self.pk)
class Room(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    connected_with = models.ForeignKey(Chats,on_delete=models.CASCADE)

class Notification(models.Model):
    user = models.ForeignKey(User,related_name='user',on_delete=models.CASCADE)
    notify_type = models.CharField(max_length=100)
    notify_user_request = models.ForeignKey(User,related_name='request',on_delete=models.CASCADE,default=None,null = True,blank=True)
    notify_post = models.ForeignKey(Post,on_delete=models.CASCADE,null = True,blank=True)
    notify_comment = models.ForeignKey(Comment,on_delete=models.CASCADE,null = True,blank=True)
    notify_reply = models.ForeignKey(Reply,on_delete=models.CASCADE,null = True,blank=True)
    notify_message = models.ForeignKey(text_Message,on_delete=models.CASCADE,default=None,blank=True,null=True)
    created_on = models.DateTimeField(auto_now_add=True)

class user_details(models.Model):
    user = models.OneToOneField(User,null=True, on_delete=models.SET_NULL,default=None)
    name = models.CharField(max_length=100)
    description = models.TextField(default='none')
    profile_image = models.TextField(default='/img/profile/default-avatar.png')
    city = models.CharField(max_length=30,default='none')
    country = models.CharField(max_length=30,default='none')
    fav_image1 = models.TextField(default='/img/profile/default-avatar.png')
    fav_image2 = models.TextField(default='/img/profile/default-avatar.png')
    fav_image3 = models.TextField(default='/img/profile/default-avatar.png')
    fav_image4 = models.TextField(default='/img/profile/default-avatar.png')
    followings = models.ManyToManyField(User,related_name='followings',blank=True)
    follower_count = models.IntegerField(default=0)
    followers = models.ManyToManyField(User,related_name='followers',blank=True)
    following_count = models.IntegerField(default=0)
    follow_requests = models.ManyToManyField(User,related_name='follow_requests',default=None,blank=True)
    worth = models.FloatField(default=0)
    post = models.ManyToManyField(Post,related_name='posts',blank=True)
    pinned = models.ManyToManyField(Post,related_name='pinned_posts',blank=True)
    notifications = models.ManyToManyField(Notification,related_name='notification',default=None,blank=True)
    notification_bell = models.BooleanField(default=False)
    phone_no = models.IntegerField(default=0)
    gender = models.CharField(max_length=10,default='None')
    status = models.CharField(max_length=100,default='Newbie')
    message_notification_count = models.IntegerField(default=0)
    privacy = models.BooleanField(default=False)

class Notepad(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

class Feeling(models.Model):
    feeling = models.CharField(max_length=100)

class Mood(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    date = models.DateTimeField(blank=True)
    date2 = models.CharField(max_length=200,default="",blank=True)
    mood = models.CharField(max_length=100)
    feelings = models.ManyToManyField(Feeling,blank=True)