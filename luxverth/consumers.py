import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .views import like_no,comment_no,reply_no
from .models import Comment as comment_table
from .models import Reply as reply_table
from .models import Post as post_table
from .models import Chats as Chat
from .models import text_Message as Message
from .views import get_last_messages, get_user_contact, get_current_chat
from channels.generic.websocket import WebsocketConsumer
import json
from django.contrib.auth.models import User
from .models import Room,Group
from luxverth.models import Notification as Notification_table
class ChatConsumer(WebsocketConsumer):
   
    def post_like(self, data):
        author = self.scope['user']
        post_id = data['post_id']
        post = post_table.objects.get(id=post_id)
        notify = False 
        if author in post.liker_users.all():
             notify = False 
        else:
            if author != post.user:
                notify = True
        
        like_count = like_no(author,post)
        print(notify)
        content = {
            'command': 'post_like',
            'post_username':post.user.username,
            'post_id': post_id,
            'like_no':like_count,
            'notify':notify
        }
        return self.send_like_response(content)
    def post_comment(self, data):
        author = self.scope['user']
        post_id = data['post_id']
        comment_text = data['comment']
        if comment_text == '':
            return 
        comment = comment_table(
            user = author,
            comment_text = data['comment'],
        )
        comment.save()
        post = post_table.objects.get(id=post_id)
        notify = False 
        if author != post.user:
            notify = True
        print(comment_text)
        
        comment_count = comment_no(comment,post)
        print(self.scope['user'].user_details.profile_image)
        content = {
            'command': 'post_comment',
            'post_id': post_id,
            'comment_no':comment_count,
            'comment_id':comment.id,
            'comment_text':comment_text,
            'notify':notify,
            'post_username':post.user.username,
            'username' : self.scope['user'].username,
            'user_name' : self.scope['user'].user_details.name,
            'user_profile_image' : self.scope['user'].user_details.profile_image
        }
        return self.send_comment_response(content)
    
    def post_reply(self, data):
        if data['comment'] == '':
            return 
        author = self.scope['user']
        post_id = data['post_id']
        post = post_table.objects.get(id=post_id)
        comment_id = data['comment_id']
        comment = comment_table.objects.get(id=comment_id)
        notify1 = False
        notify2 = False
        if author != post.user:
            notify1 = True
        if author != comment.user:
            notify2 = True  
        reply = reply_table(
            user = author,
            reply_text = data['comment'],
        )
        reply.save()
        comment_count = reply_no(reply,post,comment)
        content = {
            'notify1':notify1,
            'post_username':post.user.username,
            'notify2':notify2,
            'comment_username':comment.user.username,
            'command': 'post_reply',
            'post_id': post_id,
            'comment_id':comment_id,
            'reply_id':reply.id,
            'reply_text':reply.reply_text,
            'comment_no':comment_count,
            'username' : self.scope['user'].username,
            'user_name' : self.scope['user'].user_details.name,
            'user_profile_image' : self.scope['user'].user_details.profile_image
        }
        return self.send_reply_response(content)
    def fetch_messages(self, data):
        messages = get_last_messages(data['chatId'])
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        print('test')
        seen = ''
        if data['type'] == 'key_down':
            print('key down')
            content = {
            'type':'key_down',
            'command': 'new_message',
            'to':data['to']
            }
            return self.send_chat_message(content)
        if data['type'] == 'typing':
            content = {
            'type':'typing',
            'command': 'new_message',
            'to':data['to']
            }
            return self.send_chat_message(content)
        if data['type'] == 'seen':
            content = {
            'type':'seen',
            'command': 'new_message',
            'seen':'read',
            'to':data['to']
            }
            return self.send_chat_message(content)
        notify=False
        if data['t'] == 'group':
            group = Group.objects.get(id=data['to'])
            message = Message.objects.create(
            user=self.scope['user'],
            content=data['message']
            )
            message.save()
            group.messages.add(message)
            group.last_text_message = message
            group.save()
        else:
            user_contact = User.objects.get(username=data['to'])
            message = Message.objects.create(
            user=self.scope['user'],
            content=data['message']
            )
            current_chat = get_current_chat(user_contact,self.scope['user'])
            current_chat.messages.add(message)
            current_chat.last_text_message = message
            try:
                Room.objects.get(user=user_contact,connected_with=current_chat)
                seen='read'
            except:
                if current_chat.user1 == user_contact:
                    if current_chat.u1_status == 'read':
                        print("checking"+self.scope['user'].username)
                        user_contact.user_details.message_notification_count = user_contact.user_details.message_notification_count + 1
                    current_chat.u1_status = 'unread'
                else:
                    if current_chat.u2_status == 'read':
                        print("checking"+self.scope['user'].username)
                        user_contact.user_details.message_notification_count = user_contact.user_details.message_notification_count + 1
                    current_chat.u2_status = 'unread'
                user_contact.user_details.save()
                seen='unread'
            try:
                Room.objects.filter(user=user_contact,connected_with=current_chat)
            except:
                notification = Notification_table(
                        user = self.scope['user'],
                        notify_type = 'sent you a message',
                        notify_message=message
                    )
                notification.save()
                user_contact.user_details.notifications.add(notification)
                user_contact.user_details.notification_bell = True
                user_contact.user_details.save()
            current_chat.save()
        content = {
            'command': 'new_message',
            'to':data['to'],
            'message': self.message_to_json(message),
            'type':'none',
            'seen':seen
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'id': message.id,
            'author': message.user.username,
            'profile_image':message.user.user_details.profile_image,
            'content': message.content,
            'timestamp': str(message.timestamp.strftime("%H:%M %p"))
        }
    def send_chat_notification(self,data):
        print(data['to'])
        if data['to'] == 'group':
            data['to'] = ''
            pass
        else:
            user_contact = User.objects.get(username=data['to'])
            try:
                Room.objects.get(user=user_contact,connected_with=current_chat)
                seen='read'
            except:
                seen='unread'
        content = {
            'to':data['to'],
            'command':'send_chat_notification',
            'seen':seen
        }
        return self.send_chat_notification_response(content)
    commands = {
        'send_chat_notification':send_chat_notification,
        'fetch_messages':fetch_messages,
        'new_message':new_message,
        'post_reply':post_reply,
        'post_comment':post_comment,
        'post_like': post_like
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        if (self.room_name != 'like') and (self.room_name != 'comment')  and (self.room_name != 'reply') and (self.room_name != 'chat_list'):
            print(self.room_name)
            try:
                chat = Chat.objects.get(id=self.room_name)
                try:
                    Room.objects.get(user=self.scope['user'],connected_with=chat)
                except:
                    room = Room(
                        user = self.scope['user'],
                        connected_with = chat
                    )
                    room.save()
            except:
                pass

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        if (self.room_name != 'like') and (self.room_name != 'comment')  and (self.room_name != 'reply') and (self.room_name != 'chat_list'):
            try:
                chat = Chat.objects.get(id=self.room_name)
                Room.objects.get(user=self.scope['user'],connected_with=chat).delete()
            except:
                pass

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_like_response(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'like',
                'message': message
            }
        )
    def send_comment_response(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'comment',
                'message': message
            }
        )
    def send_reply_response(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'reply',
                'message': message
            }
        )
    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
    def send_chat_notification_response(self,message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_notifiation',
                'message': message
            }
        )
    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
    
    def chat_notifiation(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
        
    def like(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
    def comment(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
    def reply(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
