from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from node_hierarchy.serializers import NodeHierarchySerializer, NodeHierarchyMultipleSerializer
from node_hierarchy.models import NodeHierarchy
# Create your views here.

class NodeView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = NodeHierarchySerializer

    def get(self, request, pk=None, *args, **kwargs):
        nodes = self.get_objects(pk)
        serializer = NodeHierarchySerializer(nodes, many=True)
        return Response(serializer.data, status=200)

    def get_objects(self, pk):
        return NodeHierarchy.objects.filter(parent=pk)


class NodeMultipleView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = NodeHierarchyMultipleSerializer

    def get(self, request, *args, **kwargs):
        pk = request.GET.get('pk', None)
        nodes = self.get_objects(pk.split(','))
        serializer = NodeHierarchySerializer(nodes, many=True)
        return Response(serializer.data, status=200)

    def get_objects(self, pk):
        return NodeHierarchy.objects.filter(parent__in=pk)


class NodeAllView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = NodeHierarchySerializer

    def get(self, request, *args, **kwargs):
        nodes = self.get_objects()
        serializer = NodeHierarchySerializer(nodes, many=True)
        return Response(serializer.data, status=200)

    def get_objects(self):
        return NodeHierarchy.objects.all()


class NodeParentView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = NodeHierarchySerializer

    def get(self, request, *args, **kwargs):
        nodes = self.get_objects()
        serializer = NodeHierarchySerializer(nodes, many=True)
        return Response(serializer.data, status=200)

    def get_objects(self):
        return NodeHierarchy.objects.filter(parent=None)


node_multiple_view = NodeMultipleView.as_view()
node_all_view = NodeAllView.as_view()
node_view = NodeView.as_view()
node_parent_view = NodeParentView.as_view()
