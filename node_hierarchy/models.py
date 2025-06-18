from __future__ import unicode_literals

from django.db import models
from node_hierarchy.managers import NodeHierarchyManager
# Create your models here.
class NodeHierarchy(models.Model):
    NODE_CHOICES = (
        (0, 'State'),
        (1, 'District'),
        (2, 'Taluko'),
        (3, 'Village/City')
    )
    name = models.CharField(max_length=50, help_text='State/District/Taluko/Village name')
    parent = models.ForeignKey('self', related_name='parent_rel', null=True, blank=True)
    node_type = models.IntegerField(choices=NODE_CHOICES, default=3)

    objects = models.Manager() # The default manager.
    manager = NodeHierarchyManager()

    class Meta:
        app_label = 'node_hierarchy'
        ordering = ('name', )

    def __unicode__(self):
        return str(self.name) + " (" + str(self.get_node_type_display()) + ")"

    def find_children(self, node, node_id):
        nodes = self.objects.filter(parent=node)
        for n in nodes:
            if n.id == node_id:
                return node
            return self.find_children(n, node_id)