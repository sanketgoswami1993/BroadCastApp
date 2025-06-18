from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from message.models import Message, MessageDelivery, Attachment, SocialIcon, MessageCategory
from node_hierarchy.models import NodeHierarchy
from broadcasting.generic.helper import date_time_user_friendly
import json
# serializer classes here

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('id', 'file', 'file_type')


class MessageCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageCategory
        fields = ('id', 'name',)


class SocialIconSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialIcon
        read_only_fields = ('user', )
        fields = ('message', 'share', 'like')


class MessageDeliverySerializer(serializers.ModelSerializer):
    message_title = serializers.SerializerMethodField(read_only=True)
    message_text = serializers.SerializerMethodField(read_only=True)
    category = serializers.SerializerMethodField(read_only=True)
    num_attachments = serializers.SerializerMethodField(read_only=True)
    message_id = serializers.SerializerMethodField(read_only=True)
    id = serializers.IntegerField(required=True)
    user = serializers.SerializerMethodField(read_only=True)
    send_user_role = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MessageDelivery
        read_only_fields = ('message', 'message_id', 'message_title', 'message_text', 'category',
                            'num_attachments', 'user', 'created_at', 'send_user_role')
        fields = ('id', 'status', 'user', 'send_user_role', 'message_title',
                  'message_text', 'category', 'message_id', 'num_attachments', 'created_at')
        extra_kwargs = {'status': {'required': True}}

    def validate_id(self, id):
        if not MessageDelivery.objects.filter(id=id).exists():
            raise serializers.ValidationError(_("You are sent a wrong request."))
        return id

    def get_message_title(self, obj):
        try:
            return obj.message.title
        except:
            return ''

    def get_message_text(self, obj):
        try:
            return obj.message.text
        except:
            return ''

    def get_category(self, obj):
        try:
            return obj.message.category.name
        except:
            return None

    def get_num_attachments(self, obj):
        try:
            return obj.message.message_attachment_rel.select_related().count()
        except:
            return 0

    def get_message_id(self, obj):
        try:
            return obj.message.id
        except:
            return None

    def get_send_user_role(self, obj):
        try:
            return obj.message.send_user_role
        except:
            return ''

    def get_created_at(self, obj):
        try:
            return date_time_user_friendly.get_message_display(obj.message.created_at)
        except:
            return ''

    def get_user(self, obj):
        try:
            user = obj.message.user
            return {'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'from': user.user_rel.node.name + " (" + user.user_rel.node.get_node_type_display() + ")"
            }
        except:
            return {}


class MessageSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(source='message_attachment_rel', many=True, read_only=True)
    category = MessageCategorySerializer(read_only=True)
    social = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'title', 'text', 'category', 'created_at', 'attachments', 'social', 'user')


    def get_social(self, obj):
        share = obj.social_message_rel.select_related().filter(share=True).count()
        like = obj.social_message_rel.select_related().filter(like=True).count()
        requested_user = self.context.get('requested_user')
        you_liked = obj.social_message_rel.select_related().filter(like=True, user=requested_user).count()
        you_shared = obj.social_message_rel.select_related().filter(share=True, user=requested_user).count()
        return {'share': share, 'like': like, 'you_liked': you_liked, 'you_shared': you_shared}

    def get_created_at(self, obj):
        try:
            return date_time_user_friendly.get_message_display(obj.created_at)
        except:
            return ''

    def get_user(self, obj):
        try:
            user = obj.user
            return {'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'from': user.user_rel.node.name + " (" + user.user_rel.node.get_node_type_display() + ")"
            }
        except:
            return ''


class MessageCreateSerializer(serializers.ModelSerializer):
    attachments = serializers.ListField(child=
                                        serializers.FileField(allow_empty_file=False,
                                                              use_url=False), required=False)
    send_to = serializers.JSONField(required=True)
    category_id = serializers.IntegerField(required=False)

    class Meta:
        model = Message
        read_only_fields = ('user', )
        fields = ('title', 'text', 'category_id', 'attachments', 'send_to', 'send_user_role')

    def validate_send_to(self, send_to):
        sends = json.loads(send_to)
        if not type(sends) is list:
            raise serializers.ValidationError(_("It must be a list."))
        for send in sends:
            try:
                NodeHierarchy.objects.get(id=send)
            except NodeHierarchy.DoesNotExist:
                raise serializers.ValidationError(_("Node doesn't found!"))
        return sends

    def validate_category(self, category):
        try:
            MessageCategory.objects.get(pk=category)
        except MessageCategory.DoesNotExist:
            raise serializers.ValidationError(_('Invalid Message Category Selected.'))
        return category





