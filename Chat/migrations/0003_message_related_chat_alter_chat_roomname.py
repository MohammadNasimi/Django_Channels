# Generated by Django 5.0.6 on 2024-06-27 20:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Chat', '0002_chat'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='related_chat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Chat.chat'),
        ),
        migrations.AlterField(
            model_name='chat',
            name='roomname',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
