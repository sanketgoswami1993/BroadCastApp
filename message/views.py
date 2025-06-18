from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import exceptions, status

from broadcasting.generic.auth import GetUserRequested
from broadcasting.generic.utils import send_notification
from message.serializer import MessageSerializer, MessageCreateSerializer, \
    SocialIconSerializer, AttachmentSerializer, MessageDeliverySerializer, MessageCategorySerializer
from message.models import Message, MessageDelivery, SocialIcon, Attachment, MessageCategory
from node_hierarchy.models import NodeHierarchy
from info.models import UserExtend
from configure.models import Configuration
from broadcasting.generic.helper import make_error_response
from broadcasting.generic.logger import log
import threading
import json
# Create your views here.
class MessageView(GenericAPIView, GetUserRequested):
    serializer_class = MessageSerializer

    def get(self, request, pk=None, *args, **kwargs):
        user = self.get_user(request)
        results = self.paginate_queryset(self.get_queryset(user=user, pk=pk))
        serializer = self.serializer_class(results, many=True, context={'requested_user': user})
        return HttpResponse(json.dumps(serializer.data), status=200)

    def get_model(self):
        return Message

    def handle_exception(self, exc):
        if hasattr(exc, 'status_code'):
            if exc.status_code == 404:
                exc.detail = "No more messages."

        if isinstance(exc, (exceptions.NotAuthenticated,
                            exceptions.AuthenticationFailed)):
            # WWW-Authenticate header for 401 responses, else coerce to 403
            auth_header = self.get_authenticate_header(self.request)

            if auth_header:
                exc.auth_header = auth_header
            else:
                exc.status_code = status.HTTP_403_FORBIDDEN

        exception_handler = self.settings.EXCEPTION_HANDLER

        context = self.get_exception_handler_context()
        response = exception_handler(exc, context)

        if response is None:
            raise

        response.exception = True
        return response


    def get_queryset(self, user=None, pk=None):
        if pk:
            return self.get_model().objects.filter(id=pk)
        nodes = NodeHierarchy.manager.get_all_parents(user.user_rel.node).values('id')
        my_role = user.user_rel.role
        message_delivery = MessageDelivery.manager.show_user_specified_approved(my_role).filter(send_to__in=nodes).values('id') \
            if my_role in (3, 4) \
        else \
             MessageDelivery.manager.get_approved_messages().filter(send_to__in=nodes).values('id')
        return self.get_model().objects.filter(message_delivery_rel__in=message_delivery)


class MessageCategoryView(GenericAPIView):
    """
    Citizen Id proofs
    :returns list of id proofs which is approved by government.
    """
    serializer_class = MessageCategorySerializer

    def get(self, request, *args, **kwargs):
        id_proofs = self.get_queryset()
        serializer = self.serializer_class(id_proofs, many=True)
        return Response(serializer.data, status=200)

    def get_queryset(self):
        return MessageCategory.objects.all()


class MessageCreateView(CreateAPIView, GetUserRequested):
    serializer_class = MessageCreateSerializer
    parser_classes = (FormParser, MultiPartParser,)
    attachment_class = AttachmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        log.info(request.data)
        if serializer.is_valid(raise_exception=False):
            user_req = self.get_user(request)
            if user_req.user_rel.is_super_admin() or user_req.user_rel.is_controller() or \
                    user_req.user_rel.is_staff():
                response_create = self.perform_create(serializer, user_req, request)
                detail, status = self.get_response_data(response_create)

            else:
                detail, status = self.error_response(_("You don't have permission to post a message."))
        else:
            error = make_error_response(serializer)
            detail, status = self.error_response(error)

        return Response(detail, status=status)

    def get_model(self):
        return Message

    def get_response_data(self, response_create):
        if response_create:
            return {'detail': "You have posted message successfully."}, 201
        else:
            return {'detail': "Error while posting message."}, 400

    def _getattr(self, obj, key, default=None):
        return obj[key] if key in obj else default

    def error_response(self, error):
        return {'detail': error}, 400

    def notify_to_controller(self, controller, message_title):
        kwargs = settings.PUSH_NOTIFICATIONS_MESSAGE_ID.setdefault('approve-msg-controller', 0)
        send_notification(controller.user, message_title, **kwargs)

    def notify_to_all(self, controller, node, message_title, send_user_role):
        kwargs = settings.PUSH_NOTIFICATIONS_MESSAGE_ID.setdefault('msg-to-all', 0)
        kwargs['is_begin'] = True
        process = threading.Thread(target=controller.send_notification_to_under_users,
                                   args=(node, message_title, send_user_role),
                                   kwargs=kwargs)
        process.daemon = True
        process.start()

    def check_and_send(self, send_to, message, user_req):
        for send in send_to:
            node = NodeHierarchy.objects.get(id=send)
            controller = UserExtend.manager.get_controller(node)
            status = 2
            if controller:
                if controller.user.id == user_req.id and controller.can_publish_message(send):
                    status = 1
                    self.notify_to_all(controller, node, message.title, message.send_user_role)
                else:
                    self.notify_to_controller(controller, message.title)
            MessageDelivery.objects.create(message=message, send_to=node, status=status)
        return True

    def get_file_type(self, file_name):
        val = file_name.split('.')[-1]
        configure = Configuration.objects.filter(extension_allow__icontains=val)
        return configure[0].configure if configure.exists() else 0

    def upload_attachments(self, request, message):
        if request.FILES:
            files = request.FILES.getlist('attachments')
            for attachment in files:
                file_type = self.get_file_type(attachment.name)
                Attachment.objects.create(file=attachment, message=message, file_type=file_type)
        return True

    def decode_msg(self, value):
        try:
            return value.decode('unicode_escape')
        except:
            return value

    def get_category(self, data):
        category = self._getattr(data, 'category_id', None)
        try:
            return MessageCategory.objects.get(pk=category)
        except MessageCategory.DoesNotExist:
            return None

    def create_message(self, serializer, user_req):
        message_data = {
            'title': self._getattr(serializer.data, 'title'),
            'user': user_req,
            'text': self._getattr(serializer.data, 'text'),
            'send_user_role': self._getattr(serializer.data, 'send_user_role', 5),
            'category': self.get_category(serializer.data)
        }
        message_data['text'] = self.decode_msg(message_data['text'])
        message_data['title'] = self.decode_msg(message_data['title'])
        return Message.objects.create(**message_data)

    def perform_create(self, serializer, user_req=None, request=None):
        message = self.create_message(serializer, user_req)
        self.check_and_send(self._getattr(serializer.data, 'send_to'), message, user_req)
        self.upload_attachments(request, message)
        return message


class MessageDeliveryView(GenericAPIView, GetUserRequested):
    serializer_class = MessageDeliverySerializer

    def get(self, request, *args, **kwargs):
        user = self.get_user(request)
        if user.user_rel.is_controller():
            results = self.paginate_queryset(self.get_queryset(user=user))
            serializer = self.serializer_class(results, many=True)
            data, status = serializer.data, 200
            return HttpResponse(json.dumps(data), status=status)
        else:
            data, status = self.get_unauthorized_message()
        return Response(data, status=status)


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            user = self.get_user(request)
            if user.user_rel.is_controller():
                result, status = self.perform_create(serializer, user)
            else:
                result, status = self.get_unauthorized_message()
        else:
            error = make_error_response(serializer)
            result, status = self.error_response(error)

        return Response(result, status=status)

    def handle_exception(self, exc):
        if hasattr(exc, 'status_code'):
            if exc.status_code == 404:
                exc.detail = "No more pending messages."

        if isinstance(exc, (exceptions.NotAuthenticated,
                            exceptions.AuthenticationFailed)):
            # WWW-Authenticate header for 401 responses, else coerce to 403
            auth_header = self.get_authenticate_header(self.request)

            if auth_header:
                exc.auth_header = auth_header
            else:
                exc.status_code = status.HTTP_403_FORBIDDEN

        exception_handler = self.settings.EXCEPTION_HANDLER

        context = self.get_exception_handler_context()
        response = exception_handler(exc, context)

        if response is None:
            raise

        response.exception = True
        return response

    def get_model(self):
        return MessageDelivery

    def get_queryset(self, user=None):
        return self.get_model().manager.get_pending_messages(send_to=user.user_rel.node)

    def get_unauthorized_message(self):
        return {'detail': _("You are not authorized to do this.")}, 400

    def notify_to_all(self, controller, message_delivery):
        kwargs = settings.PUSH_NOTIFICATIONS_MESSAGE_ID.setdefault('msg-to-all', 0)
        kwargs['is_begin'] = True
        process = threading.Thread(target=controller.send_notification_to_under_users,
                                          args=(controller.node, message_delivery.message.title,
                                                message_delivery.message.send_user_role),
                                          kwargs=kwargs)
        process.daemon = True
        process.start()

    def notify_to_sender(self, message_delivery):
        kwargs = settings.PUSH_NOTIFICATIONS_MESSAGE_ID.setdefault('staff-msg-approve', 0)
        message = "Your message has been %s by %s." % (message_delivery.get_status_display(),
                                                       message_delivery.message.user.user_rel.node)
        process = threading.Timer(10, send_notification,
                                          args=(message_delivery.message.user, message),
                                          kwargs=kwargs)
        process.daemon = True
        process.start()

    def error_response(self, error):
        return {'detail': error}, 400

    def success_response(self, message_delivery):
        return {'detail':
                    _("%s has been %s by you.") %
                    (
                        str(message_delivery.message.title).capitalize(),
                        str(message_delivery.get_status_display()).lower()
                    )
               }, 200

    def perform_create(self, serializer, user=None):
        id, msg_status = serializer.data.pop('id'), serializer.data.pop('status')
        message_delivery = self.get_model().objects.get(id=id)
        message_delivery.status = msg_status
        message_delivery.save()
        self.notify_to_sender(message_delivery)
        if message_delivery.is_approved():
            self.notify_to_all(user.user_rel, message_delivery)
        return self.success_response(message_delivery)


class SocialView(CreateAPIView, GetUserRequested):
    serializer_class = SocialIconSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            user_req = self.get_user(request)
            self.perform_create(request.POST, user_req)
            detail, status = self.get_response_data()
        else:
            error = make_error_response(serializer)
            detail, status = self.error_response(error)

        return Response(detail, status=status)

    def get_model(self):
        return SocialIcon

    def get_response_data(self):
        return {'detail': "Success."}, 201

    def _getattr(self, obj, key, default=None):
        return obj[key] if key in obj else default

    def error_response(self, error):
        return {'detail': error}, 400

    def get_message(self, message_id):
        return Message.objects.get(id=message_id)

    def make_like(self, social_icon):
        message, created = self.get_model().objects.get_or_create(message=social_icon['message'],
                                                                  user=social_icon['user'])
        message.like = social_icon['like']
        message.save()


    def make_share(self, social_icon):
        message, created = self.get_model().objects.get_or_create(message=social_icon['message'],
                                                                  user=social_icon['user'])
        message.share = social_icon['share']
        message.save()
        return message

    def get_value(self, data, key):
        value = data.get(key, 2)
        if value:
            if value == 'false':
                value = 0
            elif value == 'true':
                value = 1
        return value

    def perform_create(self, data, user_req=None):
        social_icon = {
            'user': user_req,
        }
        message = self.get_message(self._getattr(data, 'message'))
        social_icon['message'] = message
        share, like = self.get_value(data, 'share'), self.get_value(data, 'like')
        if share in [1]:
            social_icon['share'] = share
            return self.make_share(social_icon)
        if like in [0, 1]:
            social_icon['like'] = like
            return self.make_like(social_icon)
        return None


message_view = MessageView.as_view()
message_category_view = MessageCategoryView.as_view()
message_create_view = MessageCreateView.as_view()
social_view = SocialView.as_view()
message_delivery = MessageDeliveryView.as_view()