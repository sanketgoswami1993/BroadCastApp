from django.contrib import admin
from configure.models import Configuration
# Register your models here.

class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('configure', 'maximum_attachment', 'maximum_attachment_size', 'extension_allow' )

admin.site.register(Configuration, ConfigurationAdmin)