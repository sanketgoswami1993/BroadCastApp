from django.contrib import admin
from node_hierarchy.models import NodeHierarchy
# Register your models here.

class NodeHierarchyAdmin(admin.ModelAdmin):
    search_fields = ('name', 'node_type')
    list_display = ('name', 'parent', 'node_type')

admin.site.register(NodeHierarchy, NodeHierarchyAdmin)