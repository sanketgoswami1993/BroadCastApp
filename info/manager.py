from django.db import models

class UserExtendManager(models.Manager):
    def get_controller(self, node, **kwargs):
        results = self.filter(role=2, node=node, **kwargs)
        if results.exists():
            results = results[0]
        return results

    def get_pending_staff_request(self, node, **kwargs):
        return self.filter(role=3, node=node, user__is_active=False, **kwargs)