from django.contrib import admin
from message.models import Message, Attachment, SocialIcon, MessageDelivery, MessageCategory
# Register your models here.

class MessageAdmin(admin.ModelAdmin):
    search_fields = ('user__first_name', 'user__username',
                     'user__email', 'user__last_name',
                     'title', 'text')
    list_display = ('user', 'title', 'get_status', 'send_user_role', 'created_at')

    def get_status(self, obj):
        return ', '.join(status.get_status_display()
                         for status in obj.message_delivery_rel.select_related())


class MessageDeliveryAdmin(admin.ModelAdmin):
    search_fields = ('message__user__first_name', 'message__user__username',
                     'message__user__email', 'message__user__last_name',
                     'message__title', 'message__text')
    list_display = ('message', 'status', 'send_to')


class MessageCategoryAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('name', )


class SocialIconAdmin(admin.ModelAdmin):
    search_fields = ('user__first_name', 'user__username',
                     'user__email', 'user__last_name',
                     'message__title', 'message__text')
    list_display = ('user', 'message', 'share', 'like')


admin.site.register(Message, MessageAdmin)
admin.site.register(MessageDelivery, MessageDeliveryAdmin)
admin.site.register(Attachment)
admin.site.register(MessageCategory, MessageCategoryAdmin)
admin.site.register(SocialIcon, SocialIconAdmin)
