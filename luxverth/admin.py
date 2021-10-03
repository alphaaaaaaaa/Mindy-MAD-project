from django.contrib import admin
from luxverth.models import user_details 
from luxverth.models import Post
from luxverth.models import Comment
from luxverth.models import Reply
from luxverth.models import Notification
from .models import *
# Register your models here.
admin.site.register(user_details)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Reply)
#admin.site.register(SharedPost)
admin.site.register(Notification)
admin.site.register(text_Message)
admin.site.register(Chats)
admin.site.register(Room)
admin.site.register(Group)
admin.site.register(Notepad)
admin.site.register(Mood)
admin.site.register(Feeling)