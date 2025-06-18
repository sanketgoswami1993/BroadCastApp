from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Configuration(models.Model):
    CONFIGURE_CHOICES = (
        (0, 'IMAGE'),
        (1, 'VIDEO'),
        (2, 'AUDIO'),
        (3, 'DOC'),
    )
    configure = models.IntegerField(choices=CONFIGURE_CHOICES, unique=True)
    maximum_attachment = models.IntegerField(help_text="How many attachments allowed in one message.")
    maximum_attachment_size = models.IntegerField(
        help_text="Enter size in MB, how much attachment's size allowed in one message")
    extension_allow = models.CharField(max_length=200, default='ALL',
                                       help_text="enter value comma separate.")

    class Meta:
        app_label = 'configure'

    def __unicode__(self):
        return self.get_configure_display()


