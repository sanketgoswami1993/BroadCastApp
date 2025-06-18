from django.core.mail import send_mail

import urllib
from broadcasting import settings
from push_notifications.models import GCMDevice

def sendSMS(numbers, message):
    data = urllib.urlencode({'username': settings.SMS_TEXT_LOCAL_EMAIL,
                                    'hash': settings.SMS_TEXT_LOCAL_HASH_KEY,
                                    'numbers': numbers,
                                    'message': message,
                                    'sender': settings.SENDER_NAME}
            )
    data = data.encode('utf-8')
    request = "http://api.textlocal.in/send/?"
    f = urllib.urlopen(request, data)
    fr = f.read()
    return(fr)

def send_email(subject='Your Egramsetu OTP', message='', to_email=[]):
    send_mail(subject, message, settings.FROM_EMAIL, to_email, fail_silently=True)

def send_notification(user, message, **kwargs):
    try:
        device = GCMDevice.objects.filter(user=user, user__is_active=True)
        return device.send_message(message, extra=kwargs)
    except Exception as e:
        print e

def send_notification_bulk(user_list, message, **kwargs):
    try:
        devices = GCMDevice.objects.filter(user__id__in=user_list, user__is_active=True)
        return devices.send_message(message, extra=kwargs)
    except Exception as e:
        print e

class GCMDeviceActivity(object):

    def delete_gcm_device(self, user):
        return GCMDevice.objects.filter(user=user).delete()

    def delete_reg_id_wise(self, registration_id):
        return GCMDevice.objects.filter(registration_id=registration_id).delete()

    def get_or_create_update(self, user, device_id):
        if GCMDevice.objects.filter(user=user).count() > 1:
            self.delete_gcm_device(user)
        
        gcm, is_active = GCMDevice.objects.get_or_create(user=user)
        gcm.registration_id = device_id
        gcm.active = True
        gcm.save()
        return gcm

    def create(self, user, device_id):
        self.delete_gcm_device(user)
        self.delete_reg_id_wise(device_id)
        return GCMDevice.objects.create(user=user, registration_id=device_id, active=True)

gcm_operation = GCMDeviceActivity()



