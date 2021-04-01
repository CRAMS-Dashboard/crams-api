# coding=utf-8
"""

"""
from django.conf import settings

from crams.extension.crams_aspects import CramsAspect, CRAMS_ASPECT_DICT
from crams_collection.serializers.project_serializer import ProjectSerializer


CRAMS_ASPECT_DICT[ProjectSerializer] = CramsAspect(ProjectSerializer)
