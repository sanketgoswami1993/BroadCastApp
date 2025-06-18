from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from configure.serializer import ConfigurationSerializer
from configure.models import Configuration

# Create your views here.
class ConfigureApi(GenericAPIView):
    permission_classes = (AllowAny, )
    serializer_class = ConfigurationSerializer
    model = Configuration

    def get(self, request, choice, *args, **kwargs):
        configures = self.get_queryset(choice=choice)
        serializer = self.serializer_class(configures, many=True)
        return Response(serializer.data, status=200)

    def get_queryset(self, choice=0):
        return self.model.objects.filter(configure=choice)


class ConfigureApiAll(GenericAPIView):
    permission_classes = (AllowAny, )
    serializer_class = ConfigurationSerializer
    model = Configuration

    def get(self, request, *args, **kwargs):
        configures = self.get_queryset()
        serializer = self.serializer_class(configures, many=True)
        return Response(serializer.data, status=200)

    def get_queryset(self):
        return self.model.objects.all()


configure_view = ConfigureApi.as_view()
configure_view_all = ConfigureApiAll.as_view()