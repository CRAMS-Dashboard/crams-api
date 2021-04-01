# from django.db import models
#
# from crams import models as crams_models
# from crams_allocation.models import Request
# from crams_contact import models as contact_models
#
#
# class AllocationERBLabel(crams_models.CramsCommon):
#     label = models.ForeignKey(crams_models.EResearchBodyIDKey, related_name='allocation_labels', on_delete=models.DO_NOTHING)
#
#     allocation = models.ForeignKey(Request, related_name='erb_labels', on_delete=models.DO_NOTHING)
#
#     access_restricted = models.BooleanField(default=True)
#
#     class Meta:
#         app_label = 'labels'
#         unique_together = ('label', 'allocation')
#
#     def __str__(self):
#         return '{} / {}'.format(self.label.key, self.allocation.project.title)
#
#
# class LinkedAllocationERBLabel(crams_models.CramsCommon):
#     linked_allocation = models.ForeignKey(AllocationERBLabel, related_name='linked_labels', on_delete=models.DO_NOTHING)
#
#     allocation = models.ForeignKey(Request, related_name='linked_erb_labels', on_delete=models.DO_NOTHING)
#
#     class Meta:
#         app_label = 'labels'
#
#     def __str__(self):
#         return '{} - parent: {}'.format(self.allocation.project.title, self.linked_allocation)
#
#
# class AllocationContactLabel(crams_models.CramsCommon):
#     label = models.ForeignKey(contact_models.ContactLabel, related_name='allocations', on_delete=models.DO_NOTHING)
#
#     allocation = models.ForeignKey(Request, related_name='contact_labels', on_delete=models.DO_NOTHING)
#
#     class Meta:
#         app_label = 'labels'
#
#     def __str__(self):
#         return '{} / {}'.format(self.label, self.allocation.project.title)
