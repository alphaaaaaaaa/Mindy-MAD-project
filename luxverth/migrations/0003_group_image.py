# Generated by Django 3.2.2 on 2021-05-17 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('luxverth', '0002_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='image',
            field=models.ImageField(default='/img/profile/default-avatar.png', upload_to=''),
        ),
    ]
