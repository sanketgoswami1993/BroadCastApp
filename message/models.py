from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from node_hierarchy.models import NodeHierarchy
from django.conf import settings
from message.managers import MessageDeliveryManager
# Create your models here.
class Message(models.Model):
    SEND_MESSAGE_USER_CHOICE = (
        (3, 'Staff'),
        (4, 'User'),
        (5, 'All'),
    )
    user = models.ForeignKey(User, related_name='message_user_rel')
    title = models.CharField(max_length=50)
    text = models.TextField(null=True, blank=True)
    send_user_role = models.IntegerField(choices=SEND_MESSAGE_USER_CHOICE, default=5)
    category = models.ForeignKey('MessageCategory', default=None, null=True, blank=True, related_name='category_rel')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'message'
        ordering = ('-created_at',)

    def __unicode__(self):
        return self.title


class MessageDelivery(models.Model):
    STATUS_CHOICES = (
        (0, 'Rejected'),
        (1, 'Approved'),
        (2, 'Pending'),
    )

    message = models.ForeignKey(Message, related_name='message_delivery_rel', on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=2)
    send_to = models.ForeignKey(NodeHierarchy, related_name='message_nodes_rel')

    objects = models.Manager()  # The default manager.
    manager = MessageDeliveryManager()

    class Meta:
        app_label = 'message'
        ordering = ('-id', )

    def __unicode__(self):
        return self.message.title

    def is_approved(self):
        return self.status == 1

    def is_rejected(self):
        return self.status == 0

    def is_pending(self):
        return self.status == 2


class Attachment(models.Model):
    FILE_TYPE_CHOICES = (
        (0, 'IMAGE'),
        (1, 'VIDEO'),
        (2, 'AUDIO'),
        (3, 'DOC'),
    )
    message = models.ForeignKey(Message, related_name='message_attachment_rel')
    file = models.FileField(upload_to=settings.UPLOAD_TO, verbose_name='Attachment')
    file_type = models.IntegerField(choices=FILE_TYPE_CHOICES, default=0)

    class Meta:
        app_label = 'message'
        ordering = ('-id', )

    def __unicode__(self):
        return self.file.name


class MessageCategory(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'message'

    def __unicode__(self):
        return self.name


class SocialIcon(models.Model):
    message = models.ForeignKey(Message, related_name='social_message_rel')
    user = models.ForeignKey(User, related_name='social_user_rel')
    share = models.BooleanField(default=False)
    like = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'message'
        ordering = ('-id', )

    def __unicode__(self):
        return self.message.title
