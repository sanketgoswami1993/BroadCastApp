from django.contrib import admin
from info.models import User, MyUser, UserExtend, IdentityType
# Register your models here.

class UserExtendAdmin(admin.StackedInline):
    model = UserExtend


class UserAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'email')
    list_display = ('username', 'email', 'get_node', 'get_role', 'get_contact', 'is_active')
    inlines = [UserExtendAdmin, ]

    def get_node(self, obj):
        return obj.user_rel.node

    def get_contact(self, obj):
        return obj.user_rel.contact_num

    def get_role(self, obj):
        return obj.user_rel.get_role_display()


class IdentityTypeAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )


admin.site.unregister(User)
admin.site.register(MyUser, UserAdmin)
admin.site.register(IdentityType, IdentityTypeAdmin)