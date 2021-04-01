# coding=utf-8
"""

"""
from crams.serializers import model_serializers
from crams_contact.models import ContactRole


class ContactRoleSerializer(model_serializers.ReadOnlyModelSerializer):
    """class ContactRoleSerializer."""

    class Meta(object):
        """metaclass."""

        model = ContactRole
        fields = ['id', 'name']
