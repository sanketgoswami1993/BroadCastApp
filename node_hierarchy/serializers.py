from rest_framework import serializers
from node_hierarchy.models import NodeHierarchy

class NodeHierarchySerializer(serializers.ModelSerializer):
    type_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = NodeHierarchy
        fields = ('id', 'name', 'parent', 'node_type', 'type_name')

    def get_type_name(self, obj):
        return obj.get_node_type_display()


class NodeHierarchyMultipleSerializer(serializers.ModelSerializer):
    pk = serializers.CharField(max_length=500, required=True)
    class Meta:
        model = NodeHierarchy
        fields = ('pk', 'id', 'name', 'parent', 'node_type')