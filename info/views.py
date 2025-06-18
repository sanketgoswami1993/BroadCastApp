from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import Q
from django.conf import settings

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import exceptions, status

from info.serializers import LoginSerializer, PasswordChangeSerializer, \
    UserRegistrationSerializer, IdentityTypeSerializer, \
    UserControllerRegistrationSerializer, \
    PasswordResetSerializer, PasswordResetConfirmSerializer, \
    OTPConfirmSerializer, LogoutSerializer, StaffUserActiveSerializer, UserDetailSerializer

from broadcasting.generic.auth import GetUserRequested
from broadcasting.generic.helper import make_error_response
from broadcasting.generic.utils import sendSMS, send_notification, gcm_operation, send_email

from info.models import IdentityType, UserExtend, PasswordConfirm
from node_hierarchy.models import NodeHierarchy

import random, json

# Create your views here.
class UserView(APIView):
    """
    Citizen Id proofs
    :returns list of id proofs which is approved by government.
    """
    serializer_class = UserDetailSerializer

    def get(self, request, pk=None, *args, **kwargs):
        user = self.get_objects(pk)
        serializer = UserDetailSerializer(user, many=True)
        return Response(serializer.data, status=200)

    def get_model(self):
        return User

    def get_objects(self, pk):
        return self.get_model().objects.filter(pk=pk)


class IdProofTypeView(APIView):
    """
    Citizen Id proofs
    :returns list of id proofs which is approved by government.
    """
    permission_classes = (AllowAny, )
    serializer_class = IdentityTypeSerializer

    def get(self, request, *args, **kwargs):
        id_proofs = self.get_objects()
        serializer = IdentityTypeSerializer(id_proofs, many=True)
        return Response(serializer.data, status=200)

    def get_objects(self):
        return IdentityType.objects.all()


class UserObtainAuthToken(GenericAPIView, GetUserRequested):
    """
    Login
    :except email/contact number and password
    :returns token
    """
    permission_classes = (AllowAny, )
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        # log.info(request.data)
        email = request.data.get('email')
        pwd = request.data.get('password')
        device_id = request.data.get('android_device_id')

        user = self.authenticate_email_or_ph(email=email, password=pwd)
        if user:
            if user.is_active:
                if device_id:
                    self.change_device_token(device_id, user)
                token = self.create_token(user)
                res = self.get_response_success(user, token)
                status = 200
            else:
                res = self.get_response_error(_('You are not activated.'))
                status = 400
        else:
            res = self.get_response_error(_('Invalid username and Password'))
            status = 400

        return Response(res, status=status)

    def change_device_token(self, device_id, user):
        gcm_operation.get_or_create_update(user, device_id)

    def get_response_error(self, msg):
        return {'detail': msg}

    def get_response_success(self, user, token):
        fullname = user.first_name + " " + user.last_name
        role_id, role_name = user.user_rel.role, user.user_rel.get_role_display()
        return {'token': token.key,
                'role': {'key': role_id, 'value': role_name},
                'username': fullname
        }


class LogoutView(GenericAPIView, GetUserRequested):
    """
    Logout
    :except token in header
    :returns response failure or success
    """
    serializer_class = LogoutSerializer
    token_model = Token

    def get(self, request, *args, **kwargs):
        user = self.get_user(request)
        self.flush_device_token(user)
        res, status = self.get_response_success()
        return Response(res, status=status)

    def flush_device_token(self, user):
        gcm_operation.delete_gcm_device(user)
        #user.user_rel.android_device_id = None
        #user.user_rel.save()

    def get_response_success(self):
        return {'detail': 'Logout Successfully.'}, 200


class PasswordChangeView(GenericAPIView, GetUserRequested):
    """
    Change password form.
    Accepts the following POST parameters: new_password1, new_password2
    Returns the success/fail message.
    """
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            user = self.get_user(request)
            if user.check_password(serializer.data['old_password']):
                password = serializer.data["new_password1"]
                user.set_password(password)
                user.save()
                res = {"detail": _("New password has been saved.")}
                status = 200
            else:
                res = {"detail": _("Your password is wrong.")}
                status = 400
        else:
            detail = make_error_response(serializer)
            res = {'detail': detail}
            status = 400

        return Response(res, status=status)


class PasswordResetView(GenericAPIView):
    """
    Reset password.
    Accepts the following POST parameters: email
    Returns the success/fail message.
    """
    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny, )
    token_model = Token

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            email = serializer.data.pop('email')
            user = self.get_user(email)
            response_sms = self.create_random_otp(user)
            if response_sms["status"] == "success":
                res = {"detail": _("OTP has been sent on %s." % (user.user_rel.contact_num))}
                status = 200
            else:
                res = {"detail": _(self.get_failure_response(response_sms))}
                status = 400
        else:
            detail = make_error_response(serializer)
            res = {'detail': detail}
            status = 400

        return Response(res, status=status)

    def get_user(self, email):
        return User.objects.get(Q(email=email) | Q(user_rel__contact_num=email))

    def get_failure_response(self, response_sms):
        warnings = response_sms['warnings']
        if type(warnings) is list and len(warnings) > 0:
            return response_sms["warnings"]
        else:
            return _("Message couldn't sent.")

    def sms_message(self, otp):
        return settings.FORGOT_OTP_MSG % otp

    def create_random_otp(self, user):
        otp = random.randrange(1000, 100000)
        password_confirm = PasswordConfirm.objects.create(user=user, otp=otp)
        if password_confirm:
            message = self.sms_message(otp)
            send_email(subject='Your Egramsetu OTP', message=message, to_email=[user.email])
            return json.loads(sendSMS(user.user_rel.contact_num, message))


class OTPConfirmView(GenericAPIView):
    """
    Confirm otm
    """
    serializer_class = OTPConfirmSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            otp = serializer.data.pop('otp')
            res, status = self.check_otp(otp)
        else:
            detail = make_error_response(serializer)
            res = {'detail': detail}
            status = 400
        return Response(res, status=status)

    def check_otp(self, otp):
        try:
            password_ = PasswordConfirm.objects.get(otp=otp)
            return {"detail": _("OTP is valid.")}, 200
        except PasswordConfirm.DoesNotExist:
            return {"detail": (_("You have entered a wrong or expired OTP"))}, 400


class PasswordResetConfirmView(GenericAPIView):
    """
    Reset password confirm.
    Accepts the following POST parameters: email
    Returns the success/fail message.
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (AllowAny, )
    token_model = Token

    def post(self, request, otp):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            password_confirm, is_valid = self.check_otp(otp)
            if is_valid:
                res, status = self.create_new_password(password_confirm, serializer)
            else:
                res = {"detail": password_confirm}
                status = 400
        else:
            detail = make_error_response(serializer)
            res = {'detail': detail}
            status = 400

        return Response(res, status=status)

    def create_new_password(self, password_confirm, serializer):
        user = password_confirm.user
        password = serializer.data["new_password1"]
        user.set_password(password)
        user.save()
        password_confirm.is_used = True
        password_confirm.save()
        return {"detail": _("New password has been saved.")}, 200

    def check_otp(self, otp):
        try:
            return PasswordConfirm.objects.get(otp=otp), True
        except PasswordConfirm.DoesNotExist:
            return (_("You have entered a wrong or expired OTP")), False


class RegisterView(CreateAPIView, GetUserRequested):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            user = self.perform_create(serializer)
            if user.is_active:
                detail = self.get_response_data(user)
            else:
                detail = self.get_response_inactivate(user)
            status = 201
        else:
            error = make_error_response(serializer)
            detail = self.error_response(error)
            status = 400

        return Response(detail, status=status)

    def get_response_data(self, user):
        fullname = user.first_name + " " + user.last_name
        role_id, role_name = user.user_rel.role, user.user_rel.get_role_display()
        return {'token': user.auth_token.key,
                'role': {'key': role_id, 'value': role_name},
                'username': fullname,
                'is_active': user.is_active,
        }

    def get_response_inactivate(self, user):
        return {
            'is_active': user.is_active,
            'detail': 'You are registered successfully.'
        }

    def error_response(self, error):
        return {'detail': error}

    def _getattr(self, obj, key, default=None):
        return obj[key] if key in obj else default

    def notify_message(self, user_extend):
        return '{0} has registered as {1}.'.format(user_extend.user.first_name,
                                                        user_extend.get_role_display())

    def notify(self, user_extend):
        controller = UserExtend.manager.get_controller(user_extend.node)
        if controller:
            kwargs = settings.PUSH_NOTIFICATIONS_MESSAGE_ID.setdefault('staff-register-controller', 0)
            send_notification(controller.user, self.notify_message(user_extend), **kwargs)

    def perform_create(self, serializer):
        role = serializer.data.pop('role')
        node = NodeHierarchy.objects.get(id=serializer.data.pop('node'))
        password = serializer.data.pop('password')
        user_fields = self.get_user_fields(serializer, role)
        user_extended_fields = self.get_user_extend_fields(serializer, role, node)
        user = self.create_user(user_fields, password)
        user_extend = self.create_extend_user(user_extended_fields, user)
        self.create_token(user)
        self.create_gcm_token(user, serializer)
        # notify
        if user_extend.is_staff():
            self.notify(user_extend)
        return user

    def create_extend_user(self, user_extended_fields, user):
        user_extended_fields['user'] = user
        return UserExtend.objects.create(**user_extended_fields)

    def create_user(self, user_fields, password):
        user = User.objects.create(**user_fields)
        user.set_password(password)
        user.save()
        return user

    def get_user_fields(self, serializer, role):
        return {
            'email': serializer.data.pop('email'),
            'username': serializer.data.pop('email'),
            'first_name': serializer.data.pop('first_name'),
            'last_name': serializer.data.pop('last_name'),
            'is_active': True if role == 4 else False
        }

    def get_user_extend_fields(self, serializer, role, node):
        return {
            'id_proof_type': IdentityType.objects.get(id=serializer.data.pop('id_proof_type')),
            'id_proof_num': serializer.data.pop('id_proof_num'),
            'contact_num': serializer.data.pop('contact_num'),
            'role': role,
            'designation': self._getattr(serializer.data, 'designation'),
            'node': node,
        }

    def create_gcm_token(self, user,  serializer):
        android_device_id = serializer.data.pop('android_device_id')
        return gcm_operation.create(user, android_device_id)


class CreateControllerView(CreateAPIView, GetUserRequested):
    serializer_class = UserControllerRegistrationSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            user_req = self.get_user(request)
            if user_req.user_rel.is_super_admin() or user_req.user_rel.can_create_user_for_node(
                    serializer.data['node']):
                user = self.perform_create(serializer)
                self.notify(user)
                detail = self.get_response_data(user)
                status = 201
            else:
                detail = self.error_response(_("You don't have permission to do this."))
                status = 400
        else:
            error = make_error_response(serializer)
            detail = self.error_response(error)
            status = 400

        return Response(detail, status=status)

    def notify(self, user):
        self.create_random_otp(user)

    def sms_message(self, user, otp):
        return settings.REGISTRATION_SMS_TEXT % \
               (user.user_rel.get_role_display(), user.user_rel.node, otp)

    def create_random_otp(self, user):
        otp = random.randrange(1000, 100000)
        password_confirm = PasswordConfirm.objects.create(user=user, otp=otp)
        if password_confirm:
            message = self.sms_message(user, otp)
            send_email(subject='You are created.', message=message, to_email=[user.email])
            return json.loads(sendSMS(user.user_rel.contact_num, message))

    def perform_create(self, serializer):
        user_fields = self.get_user_fields(serializer)
        user_extended_fields = self.get_user_extend_fields(serializer)
        password = serializer.data.pop('password')
        user = self.create_user(user_fields, password)
        self.create_extend_user(user_extended_fields, user)
        self.create_token(user)
        return user

    def create_extend_user(self, user_extended_fields, user):
        user_extended_fields['user'] = user
        UserExtend.objects.create(**user_extended_fields)

    def create_user(self, user_fields, password):
        user = User.objects.create(**user_fields)
        user.set_password(password)
        user.save()
        return user

    def get_user_fields(self, serializer):
        return {
            'email': serializer.data.pop('email'),
            'username': serializer.data.pop('email'),
            'first_name': serializer.data.pop('first_name'),
            'last_name': serializer.data.pop('last_name'),
        }

    def get_user_extend_fields(self, serializer):
        return {
            'id_proof_type': IdentityType.objects.get(id=serializer.data.pop('id_proof_type')),
            'id_proof_num': serializer.data.pop('id_proof_num'),
            'contact_num': serializer.data.pop('contact_num'),
            'role': serializer.data.pop('role'),
            'designation': self._getattr(serializer.data, 'designation'),
            'node': NodeHierarchy.objects.get(id=serializer.data.pop('node')),
        }

    def get_response_data(self, user):
        return {'detail': "%s %s has been created by you as a %s from %s" % (user.first_name,
                                                                             user.last_name,
                                                                             user.user_rel.get_role_display(),
                                                                             user.user_rel.node.name)}

    def error_response(self, error):
        return {'detail': error}

    def _getattr(self, obj, key, default=None):
        return obj[key] if key in obj else default


class StaffActivateView(GenericAPIView, GetUserRequested):
    serializer_class = StaffUserActiveSerializer

    def get(self, request, *args, **kwargs):
        user = self.get_user(request)
        if user.user_rel.is_controller():
            results = self.paginate_queryset(self.get_queryset(user=user))
            serializer = self.serializer_class(results, many=True)
            data, status = serializer.data, 200
        else:
            data, status = self.get_unauthorized_message()
        return Response(data, status=status)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            user = self.get_user(request)
            if user.user_rel.is_controller():
                data, status = self.perform_create(serializer)
            else:
                data, status = self.get_unauthorized_message()
        else:
            error = make_error_response(serializer)
            data, status = self.error_response(error)
        return Response(data, status=status)

    def handle_exception(self, exc):
        if hasattr(exc, 'status_code'):
            if exc.status_code == 404:
                exc.detail = "No more staff users."

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

    def perform_create(self, serializer):
        is_active = serializer.data.pop('is_active')
        id = serializer.data.pop('id')
        user_extend = self.get_staff_user(id)
        if is_active:
            return self.active_user(user_extend)
        else:
            return self.remove_user(user_extend)

    def active_user(self, user_extend):
        user_extend.user.is_active = True
        user_extend.user.save()
        kwargs = settings.PUSH_NOTIFICATIONS_MESSAGE_ID.setdefault('login', 0)
        self.notify(user_extend.user, 'You are activated.', **kwargs)
        return self.get_approve_message(user_extend.user)

    def remove_user(self, user_extend):
        u = user_extend.user
        name = u.first_name
        kwargs = settings.PUSH_NOTIFICATIONS_MESSAGE_ID.setdefault('login', 0)
        self.notify(user_extend.user, 'Your request has been rejected.', **kwargs)
        user_extend.delete()
        u.delete()
        return self.get_reject_message(name)

    def notify(self, user, message, **kwargs):
        send_notification(user, message, **kwargs)

    def get_approve_message(self, user):
        return {'detail': '%s has been activated as %s' % (user.first_name,
                                                           user.user_rel.get_role_display())}, 200

    def get_reject_message(self, name):
        return {'detail': '%s request has been rejected by you' % (name)}, 200

    def get_staff_user(self, id):
        return self.get_model().objects.get(id=id)

    def get_queryset(self, user=None):
        return self.get_model().manager.get_pending_staff_request(user.user_rel.node)

    def get_model(self):
        return UserExtend

    def get_unauthorized_message(self):
        return {'detail': _("You are not authorized to do this.")}, 400

    def error_response(self, error):
        return {'detail': error}, 400


user_get = UserView.as_view()
id_proof_list = IdProofTypeView.as_view()
obtain_auth_token = UserObtainAuthToken.as_view()
logout_view = LogoutView.as_view()
user_change_password = PasswordChangeView.as_view()
password_reset_view = PasswordResetView.as_view()
password_reset_confirm_view = PasswordResetConfirmView.as_view()
otp_valid = OTPConfirmView.as_view()
user_registration = RegisterView.as_view()
user_registration_controller = CreateControllerView.as_view()
staff_user_active = StaffActivateView.as_view()