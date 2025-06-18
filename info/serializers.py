from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.db.models import Q

from info.models import IdentityType, UserExtend
from node_hierarchy.models import NodeHierarchy
from node_hierarchy.serializers import NodeHierarchySerializer

class StaffUserActiveSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    is_active = serializers.BooleanField(required=True)
    id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(read_only=True)
    node = NodeHierarchySerializer(read_only=True)
    class Meta:
        model = UserExtend
        fields = ('id', 'is_active', 'node', 'contact_num', 'email', 'role', 'user_id')
        read_only_fields = ('user', 'node', 'role', 'contact_num', 'email', 'user_id')

    def validate_id(self, id):
        if not UserExtend.objects.filter(id=id).exists():
            raise serializers.ValidationError(_("Invalid id passed."))
        return id

    def get_user_id(self, obj):
        try: return obj.user.id
        except: return ''

class IdentityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentityType
        fields = ('id', 'name',)

class UserExtendDetailSerializer(serializers.ModelSerializer):
    node = NodeHierarchySerializer()
    id_proof_type = IdentityTypeSerializer()

    class Meta:
        model = UserExtend

class UserDetailSerializer(serializers.ModelSerializer):
    more = UserExtendDetailSerializer(source='user_rel')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'is_active', 'more')


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("email"))
    password = serializers.CharField(label=_("Password"), style={'input_type': 'password'})


class LogoutSerializer(serializers.Serializer):
    pass


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, required=True)
    new_password1 = serializers.CharField(max_length=128, required=True)
    new_password2 = serializers.CharField(max_length=128, required=True)

    def validate(self, attrs):
        password1 = attrs.get('new_password1')
        password2 = attrs.get('new_password2')

        if password1 and password2:
            if password1 != password2:
                raise serializers.ValidationError(_("The two password fields didn't match."))
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("email"), required=True)

    def validate_email(self, email):
        if not User.objects.filter(Q(email=email) | Q(user_rel__contact_num=email)).exists():
            raise serializers.ValidationError(_("You are not registered."))
        return email


class OTPConfirmSerializer(serializers.Serializer):
    otp = serializers.IntegerField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(max_length=128, required=True)
    new_password2 = serializers.CharField(max_length=128, required=True)

    def validate(self, attrs):
        password1 = attrs.get('new_password1')
        password2 = attrs.get('new_password2')

        if password1 and password2:
            if password1 != password2:
                raise serializers.ValidationError(_("The two password fields didn't match."))
        return attrs


class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer for Token model.
    """

    class Meta:
        model = Token
        fields = ('key',)


class UserRegistrationSerializer(serializers.ModelSerializer):
    ROLE_CHOICES = (
        (3, 'staff'),
        (4, 'user'),
    )
    id_proof_type = serializers.IntegerField(required=True)
    id_proof_num = serializers.CharField(max_length=20, required=True)
    contact_num = serializers.IntegerField(required=True)
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=True)
    designation = serializers.CharField(max_length=40, required=False)
    # department = serializers.IntegerField(required=True)
    node = serializers.IntegerField(required=True)
    android_device_id = serializers.CharField(max_length=200, required=True)

    class Meta:
        model = User
        read_only_fields = ('username', )
        extra_kwargs = {'first_name': {'required': True},
                        'last_name': {'required': True},
                        'email': {'required': True}}

    def validate_email(self, email):
        if User.objects.filter(email__icontains=email).exists():
            raise serializers.ValidationError(_('The email address is already taken'))
        return email

    def validate_contact_num(self, contact_num):
        if User.objects.filter(user_rel__contact_num__icontains=contact_num).exists():
            raise serializers.ValidationError(_('The contact number is already taken'))
        return contact_num

    def validate_id_proof_num(self, id_proof_num):
        if UserExtend.objects.filter(id_proof_num__icontains=id_proof_num):
            raise serializers.ValidationError(_('The ID proof number is already taken'))
        return id_proof_num

    def validate_node(self, node):
        if not NodeHierarchy.objects.filter(id=node).exists():
            raise serializers.ValidationError(_('Invalid Address added.'))
        return node


class UserControllerRegistrationSerializer(serializers.ModelSerializer):
    ROLE_CHOICES = (
        (1, 'admin'),
        (2, 'controller'),
    )
    id_proof_type = serializers.IntegerField(required=True)
    id_proof_num = serializers.CharField(max_length=20, required=True)
    contact_num = serializers.IntegerField(required=True)
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=True)
    designation = serializers.CharField(max_length=40, required=False)
    node = serializers.IntegerField(required=True)

    class Meta:
        model = User
        read_only_fields = ('username', )
        extra_kwargs = {'first_name': {'required': True},
                        'last_name': {'required': True},
                        'email': {'required': True}}

    def validate_email(self, email):
        if User.objects.filter(email__icontains=email).exists():
            raise serializers.ValidationError(_('The email address is already taken'))
        return email

    def validate_contact_num(self, contact_num):
        if User.objects.filter(user_rel__contact_num__icontains=contact_num).exists():
            raise serializers.ValidationError(_('The contact number is already taken'))
        return contact_num

    def validate_id_proof_num(self, id_proof_num):
        if UserExtend.objects.filter(id_proof_num__icontains=id_proof_num):
            raise serializers.ValidationError(_('The ID proof number is already taken'))
        return id_proof_num

    def validate_node(self, node):
        if not NodeHierarchy.objects.filter(id=node).exists():
            raise serializers.ValidationError(_('Invalid Address added.'))
        return node
