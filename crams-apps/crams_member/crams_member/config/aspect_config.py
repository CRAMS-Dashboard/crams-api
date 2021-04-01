# coding=utf-8
"""

"""
from rest_framework import exceptions

from crams.extension.crams_aspects import CRAMS_ASPECT_DICT, CramsAspect

from crams_collection.serializers.project_serializer import ProjectSerializer
from crams_member.aspects.project_contact import update_project_join_invite_request
from crams_member.aspects.project_contact import update_project_members_for_new_project_contact

if ProjectSerializer not in CRAMS_ASPECT_DICT:
    raise exceptions.APIException('Crams aspect not initialized for crams_allocation.ProjectSerializer')

project_serializer_aspect = CRAMS_ASPECT_DICT.get(ProjectSerializer)
if not isinstance(project_serializer_aspect, CramsAspect):
    msg = 'crams_member: aspect defined for crams_allocation.ProjectSerializer is not a CramsAspect object'
    raise exceptions.APIException(msg)

upd_psz_fn_name = ProjectSerializer.update_project_contacts.__name__
project_serializer_aspect.add_post_fn_for_method_name(
    method_name=upd_psz_fn_name, post_fn=update_project_members_for_new_project_contact)

upd_psz_fn_name = ProjectSerializer.update.__name__
project_serializer_aspect.add_post_fn_for_method_name(
    method_name=upd_psz_fn_name, post_fn=update_project_join_invite_request)
