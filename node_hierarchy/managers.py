from django.db import models

class NodeHierarchyManager(models.Manager):
    def get_all_parents(self, node, **kwargs):
        parents = [node.id, ]
        while node.parent:
            node = self.get(id=node.parent.id)
            parents.append(node.id)
        return self.filter(id__in=parents)
