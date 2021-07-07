from django.db import models

from crams.models import CramsCommon
from crams.models import ProjectMemberStatus
from crams_collection.models import Project
from crams_contact.models import Contact


class ProjectJoinInviteRequest(CramsCommon):
    title = models.CharField(max_length=50, blank=True, null=True)
    surname = models.CharField(max_length=200, blank=True, null=True)
    given_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(db_index=True)
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING)
    status = models.ForeignKey(ProjectMemberStatus, on_delete=models.DO_NOTHING)
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'crams_member'

    def __str__(self):  # __unicode__ on Python 2
        return self.__unicode__()

    def __unicode__(self):
        return '{} / {} / {}'.format(self.project.title,
                                     self.email,
                                     self.status.status)
