from __future__ import unicode_literals
from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from node_hierarchy.models import NodeHierarchy
from info.manager import UserExtendManager
from broadcasting.generic.utils import send_notification_bulk

# Create your models here.

class MyUser(User):
    class Meta:
        verbose_name_plural = 'Users'
        app_label = 'info'
        proxy = True


class UserExtend(models.Model):
    ROLE_CHOICES = (
        (0, 'super-admin'),
        (1, 'admin'),
        (2, 'controller'),
        (3, 'staff'),
        (4, 'user'),
    )
    user = models.OneToOneField(User, related_name='user_rel')
    id_proof_type = models.ForeignKey('IdentityType', related_name='user_id_proof_rel')
    id_proof_num = models.CharField(max_length=20, unique=True)
    contact_num = models.CharField(max_length=10, unique=True)
    role = models.IntegerField(choices=ROLE_CHOICES, default=4)
    designation = models.CharField(max_length=40, null=True, blank=True)
    node = models.ForeignKey(NodeHierarchy, related_name='user_node_rel')

    objects = models.Manager()
    manager = UserExtendManager()

    class Meta:
        app_label = 'info'
        ordering = ('-id', )

    def __unicode__(self):
        return self.user.username

    def is_super_admin(self):
        return self.role == 0

    def is_admin(self):
        return self.role == 1

    def is_controller(self):
        return self.role == 2

    def is_staff(self):
        return self.role == 3

    @property
    def is_active(self):
        return self.user.is_active

    @property
    def email(self):
        return self.user.email

    def find_children_node(self, node, node_id):
        nodes = NodeHierarchy.objects.filter(parent=node)
        for n in nodes:
            if n.id == node_id:
                return n
            self.find_children_node(n, node_id)

    def can_create_user_for_node(self, node_id):
        if self.role == 1:
            return self.node.id == node_id or self.find_children_node(self.node, node_id)
        return False

    def can_publish_message(self, node_id):
        if self.role == 2:
            return self.node.id == node_id or self.find_children_node(self.node, node_id)
        return False

    def send_to_user(self, n, message, send_user_role, is_begin, **kwargs):
        users = n.user_node_rel.select_related()
        if is_begin:
            users = users.exclude(role=2)
        if not send_user_role == 5:
            users = users.filter(role=send_user_role)
        user_list = users.values_list('user')
        send_notification_bulk(user_list, message, **kwargs)

    def send_notification_to_under_users(self, node, message, send_user_role, is_begin=False, **kwargs):
        if is_begin:
            self.send_to_user(node, message, send_user_role, is_begin, **kwargs)
            is_begin=False
        nodes = NodeHierarchy.objects.filter(parent=node)
        for node in nodes:
            self.send_to_user(node, message, send_user_role, is_begin, **kwargs)
            self.send_notification_to_under_users(node, message, send_user_role, is_begin, **kwargs)


class IdentityType(models.Model):
    name = models.CharField(max_length=40, unique=True)

    class Meta:
        app_label = 'info'
        ordering = ('-id', )

    def __unicode__(self):
        return self.name


# class Department(models.Model):
#     name = models.CharField(max_length=40, unique=True)
#
#     class Meta:
#         app_label = 'info'
#
#     def __unicode__(self):
#         return self.name

class PasswordConfirm(models.Model):
    user = models.ForeignKey(User, related_name='password_confirm_rel')
    otp = models.IntegerField()
    is_used = models.BooleanField(default=False)
    expired_at = models.DateTimeField(default=datetime.now() + timedelta(days=1))

    class Meta:
        app_label = 'info'
        ordering = ('-id', )

    def __unicode__(self):
        return self.user.email

#Signals
def clean_password_confirm_model(sender, instance, **kwargs):
    if instance.is_used:
        instance.delete()
    ## Delete Expired OTP tokens
    PasswordConfirm.objects.filter(expired_at__lte=datetime.now()).delete()

models.signals.post_save.connect(clean_password_confirm_model, sender=PasswordConfirm)