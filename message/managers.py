from django.db import models

class MessageDeliveryManager(models.Manager):

    def get_approved_messages(self, **kwargs):
        return self.filter(status=1, **kwargs)

    def show_user_specified_approved(self, my_role, **kwargs):
        # 3 - staff , 4 - User
        return self.filter(models.Q(status=1),
                           models.Q(message__send_user_role=my_role) |
                           models.Q(message__send_user_role=5), **kwargs)

    def get_pending_messages(self, **kwargs):
        return self.filter(status=2, **kwargs)